'''Hypertrace instrumentation logic for aiohttp-client'''
import logging
import traceback
import types
import typing
from collections import deque
import asyncio
import aiohttp
import wrapt
from opentelemetry import context as context_api
from opentelemetry import trace
from opentelemetry.instrumentation.aiohttp_client.version import __version__
from opentelemetry.trace import TracerProvider, get_tracer
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from hypertrace.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)  # pylint: disable=C0103

# Max time to wait for response data to be read.
MAX_WAIT_TIME = 0.1 # seconds

# aiohttp-client instrumentation module wrapper class
class AioHttpClientInstrumentorWrapper(AioHttpClientInstrumentor, BaseInstrumentorWrapper):
    """Hypertrace wrapper class around OpenTelemetry AioHttpClient Instrumentor class"""
    # Constructor
    def __init__(self):
        '''Constructor'''
        logger.debug('Entering AioHttpClientInstrumentor.__init__().')
        super().__init__()

    def _instrument(self, **kwargs) -> None:
        '''Enable instrumentation.'''
        logger.debug(
            'Entering AioHttpClientInstrumentorWrapper._instrument().')
        # Initialize OTel instrumentor
        super()._instrument(
            tracer_provider=kwargs.get("tracer_provider"),
            url_filter=kwargs.get("url_filter"),
            span_name=kwargs.get('span_name')
        )
        # Initialize HyperTrace instrumentor
        _instrument(
            tracer_provider=kwargs.get("tracer_provider"),
            url_filter=kwargs.get("url_filter"),
            span_name=kwargs.get("span_name"),
            aiohttp_client_wrapper=self
        )

# aliases for type definitions
_UrlFilterT = typing.Optional[typing.Callable[[  # pylint: disable=unsubscriptable-object
    str], str]]
_SpanNameT = typing.Optional[  # pylint: disable=unsubscriptable-object
    typing.Union[typing.Callable[[aiohttp.TraceRequestStartParams],  # pylint: disable=unsubscriptable-object
                                 str], str]
]

# build an aiohttp trace config


def create_trace_config(
        url_filter: _UrlFilterT = None,
        span_name: _SpanNameT = None,
        tracer_provider: TracerProvider = None,
        aiohttp_client_wrapper: AioHttpClientInstrumentorWrapper = None
) -> aiohttp.TraceConfig:
    '''Build an aiohttp-client trace config for use with Hypertrace'''
    tracer = get_tracer(__name__, __version__, tracer_provider)

    # https://docs.aiohttp.org/en/stable/tracing_reference.html describes
    # the events/signals and handlers that can be registered
    # This runs after each chunk of request data is sent
    async def on_request_chunk_sent(
            unused_session: aiohttp.ClientSession,
            trace_config_ctx: types.SimpleNamespace,
            params: aiohttp.TraceRequestChunkSentParams
    ):
        logger.debug('Entering hypertrace on_request_chunk_sent().')
        if hasattr(params, 'chunk') and params.chunk is not None:
            decoded_chunk = params.chunk.decode()
            logger.debug('request chunk: %s', decoded_chunk)
            trace_config_ctx.request_body += decoded_chunk

    # This runs after an exception occurs
    async def on_request_exception( # pylint: disable=W0613
            unused_session: aiohttp.ClientSession,
            trace_config_ctx: types.SimpleNamespace,
            params: aiohttp.TraceRequestExceptionParams,
    ):
        logger.debug('Entering on_request_exception().')


    # This runs after the request
    async def on_request_end(
            unused_session: aiohttp.ClientSession,
            trace_config_ctx: types.SimpleNamespace,
            params: aiohttp.TraceRequestEndParams,
    ) -> None:
        logger.debug('Entering hypertrace on_request_end().')
        # utf8_decoder = codecs.getincrementaldecoder('utf-8')
        response_body = b''
        if hasattr(params.response, 'content') \
          and params.response.content is not None:
            content_stream = params.response.content
            # A temporary dual end queue to copy data into
            # and use to reset the stream.
            tmp_deque = deque()
            # Read all the data in the response buffer. This
            # will block until it receives the expected number of bytes
            # or the connection times out and move on with already read data.
            logger.debug('Reading data---->')
            try:
                while not content_stream.at_eof():
                    response_chunk = b''
                    response_chunk = await asyncio.wait_for(
                       content_stream.read(),
                       MAX_WAIT_TIME
                    )
                    tmp_deque.append(response_chunk)
                    response_body += response_chunk
            except asyncio.TimeoutError as err: # pylint: disable=W0703
                logger.error('No data to display, exception=%s, stacktrace=%s',
                             err,
                             traceback.print_exc())
            finally:
                logger.debug('response_body: %s', str(response_body))
                # Reset response.content_stream
                content_stream._cursor = 0 # pylint: disable=W0212
                content_stream._buffer = tmp_deque # pylint: disable=W0212
        request_body = ''
        if hasattr(trace_config_ctx, 'request_body') and trace_config_ctx.request_body is not None:
            request_body = trace_config_ctx.request_body
        span = trace.get_current_span()
        # Add headers & body to span
        if span.is_recording():
            aiohttp_client_wrapper.generic_request_handler(
                params.headers, request_body, span)
            aiohttp_client_wrapper.generic_response_handler(
                params.response.headers, response_body, span)
        trace_config_ctx.end_callback_called = True
        trace_config_ctx.span = span

    def _trace_config_ctx_factory(**kwargs):
        kwargs.setdefault("trace_request_ctx", {})
        return types.SimpleNamespace(
            span_name=span_name,\
            tracer=tracer, \
            url_filter=url_filter, \
            **kwargs, \
            request_body='', \
        )

    trace_config = aiohttp.TraceConfig(
        trace_config_ctx_factory=_trace_config_ctx_factory
    )

    trace_config.on_request_chunk_sent.append(on_request_chunk_sent)
    trace_config.on_request_end.append(on_request_end)
    trace_config.on_request_exception.append(on_request_exception)

    return trace_config

def _instrument(
        tracer_provider: TracerProvider = None,
        url_filter: _UrlFilterT = None,
        span_name: _SpanNameT = None,
        aiohttp_client_wrapper: AioHttpClientInstrumentorWrapper = None
) -> None:
    '''Setup details of trace config context'''
    def instrumented_init(wrapped, instance, args, kwargs) -> None:  # pylint: disable=W0613
        if context_api.get_value("suppress_instrumentation"):
            return wrapped(*args, **kwargs)

        trace_configs = list(kwargs.get("trace_configs") or ())

        trace_config = create_trace_config(
            url_filter=url_filter,
            span_name=span_name,
            tracer_provider=tracer_provider,
            aiohttp_client_wrapper=aiohttp_client_wrapper
        )
        trace_configs.append(trace_config)

        kwargs["trace_configs"] = trace_configs
        return wrapped(*args, **kwargs)

    wrapt.wrap_function_wrapper(
        aiohttp.ClientSession, "__init__", instrumented_init
    )
