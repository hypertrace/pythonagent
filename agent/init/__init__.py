import logging
import yaml
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleExportSpanProcessor
from config import HypertraceConfig
from instrumentation.flask import FlaskInstrumentorWrapper

class AgentInit:
  
  def __init__(self):
    logging.debug('Initializing AgentInit object.')
    self._moduleInitialized = {
      "flask": False,
      "grpc": False 
    }
    self._hypertraceConfig = HypertraceConfig()
    self._flaskInstrumentorWrapper = None

  def dumpConfig(self):
    logging.debug('Calling DumpConfig().')
    for m in self._moduleInitialized:
      logging.debug(m + ':' + str(self._moduleInitialized[m]))

  def flaskInit(self, app):
    logging.debug('Calling AgentInit.flaskInit().')
    logging.debug("Dump config inside flaskInit :"+ str(self._hypertraceConfig.DATA_CAPTURE_HTTP_BODY_REQUEST));
    self._moduleInitialized['flask'] = True
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
      SimpleExportSpanProcessor(ConsoleSpanExporter())
    )
    self._flaskInstrumentorWrapper = FlaskInstrumentorWrapper()
    self._flaskInstrumentorWrapper.instrument_app(app)
    self._flaskInstrumentorWrapper.setProcessRequestHeaders(self._hypertraceConfig.DATA_CAPTURE_HTTP_HEADERS_REQUEST)
    self._flaskInstrumentorWrapper.setProcessResponseHeaders(self._hypertraceConfig.DATA_CAPTURE_HTTP_HEADERS_RESPONSE)
    self._flaskInstrumentorWrapper.setProcessRequestBody(self._hypertraceConfig.DATA_CAPTURE_HTTP_BODY_REQUEST)
    self._flaskInstrumentorWrapper.setProcessResponseBody(self._hypertraceConfig.DATA_CAPTURE_HTTP_BODY_REQUEST)
    RequestsInstrumentor().instrument()
