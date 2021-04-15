import sys
import os.path
import logging
import traceback
import types
import typing
import aiohttp
import wrapt
import codecs
from opentelemetry import context as context_api
from opentelemetry import trace
from opentelemetry.instrumentation.aiohttp_client.version import __version__
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import SpanKind, TracerProvider, get_tracer
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from hypertrace.agent.instrumentation import BaseInstrumentorWrapper

#Initialize logger with local module name
logger = logging.getLogger(__name__)

# aiohttp-client instrumentation module wrapper class
class AioHttpClientInstrumentorWrapper(AioHttpClientInstrumentor, BaseInstrumentorWrapper):
  # Constructor
  def __init__(self):
    logger.debug('Entering AioHttpClientInstrumentor.__init__().')
    super().__init__()

  def _instrument(self, **kwargs):
    logger.debug('Entering AioHttpClientInstrumentorWrapper._instrument().')
    # Initialize OTel instrumentor
    super()._instrument(
      tracer_provider=kwargs.get("tracer_provider"),
      url_filter=kwargs.get("url_filter"),
      span_name=kwargs.get("span_name"),
    )
    # Initialize HyperTrace instrumentor
    _instrument(
      tracer_provider=kwargs.get("tracer_provider"),
      url_filter=kwargs.get("url_filter"),
      span_name=kwargs.get("span_name"),
      aioHttpClientWrapper=self
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
    aioHttpClientWrapper: AioHttpClientInstrumentorWrapper = None
) -> aiohttp.TraceConfig:

    tracer = get_tracer(__name__, __version__, tracer_provider)

    # This runs after each chunk of request data is sent
    async def on_request_chunk_sent(
        unused_session: aiohttp.ClientSession,
        trace_config_ctx: types.SimpleNamespace,
        params: aiohttp.TraceRequestChunkSentParams
    ):
       logger.debug('Entering hypertrace on_request_chunk_sent().')
       decodedChunk = params.chunk.decode()
       logger.debug('request chunk: ' + decodedChunk)
       if hasattr(params, 'chunk') and params.chunk is not None:
         trace_config_ctx.requestBody += decodedChunk
       
    # This runs after the request
    async def on_request_end(
        unused_session: aiohttp.ClientSession,
        trace_config_ctx: types.SimpleNamespace,
        params: aiohttp.TraceRequestEndParams,
    ):
       logger.debug('Entering hypertrace on_request_end().')
       logger.debug('request headers: ' + str(params.headers))
       logger.debug('response headers: ' + str(params.response.headers))
       Utf8Decoder = codecs.getincrementaldecoder('utf-8')
       responseBody = ''
       if hasattr(params.response, 'content'):
         contentStream = params.response.content
         while not contentStream.at_eof():
           responseBody = await contentStream.read()
         logger.debug('responseBody: ' + str(responseBody))
       requestBody = ''
       if hasattr(trace_config_ctx, 'requestBody') and trace_config_ctx.requestBody is not None:
         logger.debug('requestBody: ' + trace_config_ctx.requestBody)
         requestBody = trace_config_ctx.requestBody
       span = trace.get_current_span()
       logger.debug('Found span: ' + str(span))
       # Add headers & body to span
       if span.is_recording():
         requestHeaders = [(k, v) for k, v in params.headers.items()]
         aioHttpClientWrapper.genericRequestHandler(requestHeaders, requestBody, span)
         responseHeaders = [(k, v) for k, v in params.response.headers.items()]
         aioHttpClientWrapper.genericResponseHandler(responseHeaders, responseBody, span)

    def _trace_config_ctx_factory(**kwargs):
        kwargs.setdefault("trace_request_ctx", {})
        return types.SimpleNamespace(
            span_name=span_name, tracer=tracer, url_filter=url_filter, **kwargs, requestBody=''
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
    aioHttpClientWrapper: AioHttpClientInstrumentorWrapper = None
):
    def instrumented_init(wrapped, instance, args, kwargs):
        if context_api.get_value("suppress_instrumentation"):
            return wrapped(*args, **kwargs)

        trace_configs = list(kwargs.get("trace_configs") or ())

        trace_config = create_trace_config(
            url_filter=url_filter,
            span_name=span_name,
            tracer_provider=tracer_provider,
            aioHttpClientWrapper=aioHttpClientWrapper
        )
        trace_configs.append(trace_config)

        kwargs["trace_configs"] = trace_configs
        return wrapped(*args, **kwargs)

    wrapt.wrap_function_wrapper(
        aiohttp.ClientSession, "__init__", instrumented_init
    )

