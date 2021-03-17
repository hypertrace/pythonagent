import logging
import sys
import os
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleExportSpanProcessor
from config import HypertraceConfig
from instrumentation.flask import FlaskInstrumentorWrapper
from instrumentation.grpc import GrpcInstrumentorServerWrapper,GrpcInstrumentorClientWrapper
from opentelemetry.sdk.resources import Resource

logger = logging.getLogger(__name__)

class AgentInit:
  
  def __init__(self):
    logger.debug('Initializing AgentInit object.')
    self._moduleInitialized = {
      "flask": False,
      "grpc": False,
      "mysql": False,
      "postgresql": False
    }
    try:
      self._hypertraceConfig = HypertraceConfig()
      self._tracerProvider = TracerProvider(
        resource=Resource.create({
            "service.name": self._hypertraceConfig.DATA_CAPTURE_SERVICE_NAME,
            "service.instance.id": os.getpid(),
        })
      )
#      self._tracerProvider = trace.get_tracer('tester')
      trace.set_tracer_provider(self._tracerProvider)
      self._consoleSpanExporter = ConsoleSpanExporter(service_name='tester')
      self._simpleExportSpanProcessor = SimpleExportSpanProcessor(self._consoleSpanExporter)
      trace.get_tracer_provider().add_span_processor(self._simpleExportSpanProcessor)
#      self._tracerProvider.add_span_processor(self._simpleExportSpanProcessor)
      self._requestsInstrumentor = RequestsInstrumentor()
      self._flaskInstrumentorWrapper = None
      self._grpcInstrumentorClientWrapper = None
      self._grpcInstrumentorServerWrapper = None
    except:
      logger.error('Failed to initialize opentelemetry: exception=%s, stacktrace=%s', sys.exc_info()[0], traceback.format_exc())
      raise e 

  def dumpConfig(self):
    logger.debug('Calling DumpConfig().')
    for m in self._moduleInitialized:
      logger.debug(m + ':' + str(self._moduleInitialized[m]))

  def flaskInit(self, app):
    logger.debug('Calling AgentInit.flaskInit().')
    try:
      logger.debug('Dump config inside flaskInit :' + str(self._hypertraceConfig.DATA_CAPTURE_HTTP_BODY_REQUEST));
      self._moduleInitialized['flask'] = True
      self._flaskInstrumentorWrapper = FlaskInstrumentorWrapper()
      self._flaskInstrumentorWrapper.instrument_app(app)
      self._flaskInstrumentorWrapper.setServiceName(self._hypertraceConfig.DATA_CAPTURE_SERVICE_NAME)
      self._flaskInstrumentorWrapper.setProcessRequestHeaders(self._hypertraceConfig.DATA_CAPTURE_HTTP_HEADERS_REQUEST)
      self._flaskInstrumentorWrapper.setProcessResponseHeaders(self._hypertraceConfig.DATA_CAPTURE_HTTP_HEADERS_RESPONSE)
      self._flaskInstrumentorWrapper.setProcessRequestBody(self._hypertraceConfig.DATA_CAPTURE_HTTP_BODY_REQUEST)
      self._flaskInstrumentorWrapper.setProcessResponseBody(self._hypertraceConfig.DATA_CAPTURE_HTTP_BODY_REQUEST)
    except:
      logger.debug('Failed to initialize flask instrumentation wrapper: exception=%s, stacktrace=%s', sys.exc_info()[0], traceback.format_exc())
      raise e

  def grpcInit(self):
    logger.debug('Calling AgentInit.grpcInit')
    try:
      self._moduleInitialized['grpc'] = True
      self._grpcInstrumentorClientWrapper = GrpcInstrumentorClientWrapper()
      self._grpcInstrumentorServerWrapper = GrpcInstrumentorServerWrapper()
      self._grpcInstrumentorClientWrapper.instrument()
      self._grpcInstrumentorServerWrapper.instrument()
      self._grpcInstrumentorClientWrapper.setProcessRequestHeaders(self._hypertraceConfig.DATA_CAPTURE_RPC_METADATA_REQUEST)
      self._grpcInstrumentorClientWrapper.setProcessResponseHeaders(self._hypertraceConfig.DATA_CAPTURE_RPC_METADATA_RESPONSE)
      self._grpcInstrumentorClientWrapper.setProcessRequestBody(self._hypertraceConfig.DATA_CAPTURE_RPC_BODY_REQUEST)
      self._grpcInstrumentorClientWrapper.setProcessResponseBody(self._hypertraceConfig.DATA_CAPTURE_RPC_BODY_REQUEST)
      self._grpcInstrumentorServerWrapper.setProcessRequestHeaders(self._hypertraceConfig.DATA_CAPTURE_RPC_METADATA_REQUEST)
      self._grpcInstrumentorServerWrapper.setProcessResponseHeaders(self._hypertraceConfig.DATA_CAPTURE_RPC_METADATA_RESPONSE)
      self._grpcInstrumentorServerWrapper.setProcessRequestBody(self._hypertraceConfig.DATA_CAPTURE_RPC_BODY_REQUEST)
      self._grpcInstrumentorServerWrapper.setProcessResponseBody(self._hypertraceConfig.DATA_CAPTURE_RPC_BODY_REQUEST)
    except:
      logger.debug('Failed to initialize grpc instrumentation wrapper: exception=%s, stacktrace=%s', sys.exc_info()[0], traceback.format_exc())
      raise e

  def globalInit(self):
    logger.debug('Calling AgentInit.globalInit().')
    try:
      self._requestsInstrumentor.instrument()
    except:
      logger.debug('Failed global init: exception=%s, stacktrace=%s', sys.exc_info()[0], traceback.format_exc())
      raise e
