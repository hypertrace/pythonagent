from opentelemetry import trace
#from opentelemetry.instrumentation.flask import FlaskInstrumentor
# The HyperTrace wrapper around the opentelementry flask instrumentation wrapper
from instrumentation.flask import FlaskInstrumentorWrapper
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
#from config import HypertraceConfig
#from config import EnvironmentConfig
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
)
import logging

class AgentInit:
  def __init__(self):
    logging.debug('Initializing AgentInit object.')
    self._moduleInitialized = {
      "flask": False,
      "grpc": False 
    }
    self._flaskInstrumentorWrapper = None

  def dumpConfig(self):
    logging.debug('Calling DumpConfig().')
    for m in self._moduleInitialized:
      logging.debug(m + ':' + str(self._moduleInitialized[m]))

  def flaskInit(self, app):
    logging.debug('Calling AgentInit.flaskInit().')
    self._moduleInitialized['flask'] = True
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
      SimpleExportSpanProcessor(ConsoleSpanExporter())
    )
    self._flaskInstrumentorWrapper = FlaskInstrumentorWrapper()
    self._flaskInstrumentorWrapper.instrument_app(app)
    self._flaskInstrumentorWrapper.setProcessRequestHeaders(True)
    self._flaskInstrumentorWrapper.setProcessResponseHeaders(True)
    self._flaskInstrumentorWrapper.setProcessRequestBody(True)
    self._flaskInstrumentorWrapper.setProcessResponseBody(True)
    RequestsInstrumentor().instrument()

  def flaskRequest(self, name, url):
    tracer = trace.get_tracer('tester')
    with tracer.start_as_current_span(name):
      requests.get(url)
