'''Hypertrace instrumentation logic for aiohttp-client'''
import sys
import os.path
import logging
import traceback
import types
import typing
import codecs
import aiohttp
import wrapt
from opentelemetry import context as context_api
from opentelemetry import trace
from opentelemetry.instrumentation.aiohttp_client.version import __version__
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import SpanKind, TracerProvider, get_tracer
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from hypertrace.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__)  # pylint: disable=C0103

def hypertrace_name_callback(trace_request_start_params):
    '''Generate span name'''
    logger.debug('Entering hypertrace_name_callback(), method=%s, url=%s.',
                 trace_request_start_params.method,
                 str(trace_request_start_params.url))
    return trace_request_start_params.method + ' ' + str(trace_request_start_params.url)

# aiohttp-client instrumentation module wrapper class
class AioHttpClientInstrumentorWrapper(AioHttpClientInstrumentor, BaseInstrumentorWrapper):
    '''Hypertrace wrapper class around OpenTelemetry AioHttpClient Instrumentor class'''
    # Constructor
    def __init__(self):
        logger.debug('Entering AioHttpClientInstrumentor.__init__().')
        super().__init__()

    def _instrument(self, **kwargs):
        logger.debug(
            'Entering AioHttpClientInstrumentorWrapper._instrument().')
        # Initialize OTel instrumentor
        super()._instrument(
            tracer_provider=kwargs.get("tracer_provider"),
            url_filter=kwargs.get("url_filter"),
            span_name=hypertrace_name_callback
        )
        # Initialize HyperTrace instrumentor
        _instrument(
            tracer_provider=kwargs.get("tracer_provider"),
            url_filter=kwargs.get("url_filter"),
            span_name=kwargs.get("span_name"),
            aiohttp_client_wrapper=self
        )

    # disable instrumentation of aiohttp
    def _uninstrument(self, **kwargs):
        super()._uninstrument(kwargs)


# aliases for type definitions
_UrlFilterT = typing.Optional[typing.Callable[[str], str]]
_SpanNameT = typing.Optional[
    typing.Union[typing.Callable[[aiohttp.TraceRequestStartParams], str], str]
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

    # This runs after the request
    async def on_request_end(
            unused_session: aiohttp.ClientSession,
            trace_config_ctx: types.SimpleNamespace,
            params: aiohttp.TraceRequestEndParams,
    ):
        logger.debug('Entering hypertrace on_request_end().')
        logger.debug('request headers: %s', str(params.headers))
        logger.debug('response headers: %s', str(params.response.headers))
        # utf8_decoder = codecs.getincrementaldecoder('utf-8')
        response_body = ''
        if hasattr(params.response, 'content'):
            content_stream = params.response.content
            while not content_stream.at_eof():
                response_body = await content_stream.read()
            logger.debug('response_body: %s', str(response_body))
        request_body = ''
        if hasattr(trace_config_ctx, 'request_body') and trace_config_ctx.request_body is not None:
            logger.debug('request_body: %s', trace_config_ctx.request_body)
            request_body = trace_config_ctx.request_body
        span = trace.get_current_span()
        logger.debug('Found span: %s', str(span))
        # Add headers & body to span
        if span.is_recording():
            request_headers = [(k, v) for k, v in params.headers.items()] # pylint: disable=R1721
            aiohttp_client_wrapper.generic_request_handler(
                request_headers, request_body, span)
            response_headers = [(k, v)
                                for k, v in params.response.headers.items()] # pylint: disable=R1721
            aiohttp_client_wrapper.generic_response_handler(
                response_headers, response_body, span)

    def _trace_config_ctx_factory(**kwargs):
        kwargs.setdefault("trace_request_ctx", {})
        return types.SimpleNamespace(
            span_name=span_name, tracer=tracer, url_filter=url_filter, **kwargs, request_body=''
        )

    trace_config = aiohttp.TraceConfig(
        trace_config_ctx_factory=_trace_config_ctx_factory
    )

    trace_config.on_request_chunk_sent.append(on_request_chunk_sent)
    trace_config.on_request_end.append(on_request_end)

    return trace_config

def _instrument(
        tracer_provider: TracerProvider = None,
        url_filter: _UrlFilterT = None,
        span_name: _SpanNameT = None,
        aiohttp_client_wrapper: AioHttpClientInstrumentorWrapper = None
):
    '''Setup details of trace config context'''
    def instrumented_init(wrapped, instance, args, kwargs): # pylint: disable=W0613
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
