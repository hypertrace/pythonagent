import logging
import yaml
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleExportSpanProcessor
from config import HypertraceConfig
from instrumentation.flask import FlaskInstrumentorWrapper
from instrumentation.grpc import GrpcInstrumentorServerWrapper,GrpcInstrumentorClientWrapper

logger = logging.getLogger(__name__)

class AgentInit:
  
  def __init__(self):
    logger.debug('Initializing AgentInit object.')
    self._moduleInitialized = {
      "flask": False,
      "grpc": False 
    }
    self._hypertraceConfig = HypertraceConfig()
    self._tracerProvider = TracerProvider()
    trace.set_tracer_provider(self._tracerProvider)
    self._consoleSpanExporter = ConsoleSpanExporter()
    self._simpleExportSpanProcessor = SimpleExportSpanProcessor(self._consoleSpanExporter)
    trace.get_tracer_provider().add_span_processor(self._simpleExportSpanProcessor)
    self._requestsInstrumentor = RequestsInstrumentor()
    self._flaskInstrumentorWrapper = None
    self._grpcInstrumentorClientWrapper = None
    self._grpcInstrumentorServerWrapper = None

  def dumpConfig(self):
    logger.debug('Calling DumpConfig().')
    for m in self._moduleInitialized:
      logger.debug(m + ':' + str(self._moduleInitialized[m]))

  def flaskInit(self, app):
    logger.debug('Calling AgentInit.flaskInit().')
    logger.debug("Dump config inside flaskInit :"+ str(self._hypertraceConfig.DATA_CAPTURE_HTTP_BODY_REQUEST));
    self._moduleInitialized['flask'] = True
    self._flaskInstrumentorWrapper = FlaskInstrumentorWrapper()
    self._flaskInstrumentorWrapper.instrument_app(app)
    self._flaskInstrumentorWrapper.setProcessRequestHeaders(self._hypertraceConfig.DATA_CAPTURE_HTTP_HEADERS_REQUEST)
    self._flaskInstrumentorWrapper.setProcessResponseHeaders(self._hypertraceConfig.DATA_CAPTURE_HTTP_HEADERS_RESPONSE)
    self._flaskInstrumentorWrapper.setProcessRequestBody(self._hypertraceConfig.DATA_CAPTURE_HTTP_BODY_REQUEST)
    self._flaskInstrumentorWrapper.setProcessResponseBody(self._hypertraceConfig.DATA_CAPTURE_HTTP_BODY_REQUEST)

  def grpcInit(self):
    logger.debug('Calling AgentInit.grpcInit')
    self._moduleInitialized['grpc'] = True
    self._grpcInstrumentorClientWrapper = GrpcInstrumentorClientWrapper()
    self._grpcInstrumentorServerWrapper = GrpcInstrumentorServerWrapper()
    self._grpcInstrumentorClientWrapper.instrument()
    self._grpcInstrumentorServerWrapper.instrument()

  def globalInit(self):
    logger.debug('Calling AgentInit.globalInit().')
    self._requestsInstrumentor.instrument()
