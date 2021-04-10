import sys
import os.path
import logging
import traceback
from agent.instrumentation import BaseInstrumentorWrapper
from opentelemetry.instrumentation.requests import RequestsInstrumentor

#Initialize logger with local module name
logger = logging.getLogger(__name__)

# The main entry point 
class RequestsInstrumentorWrapper(RequestsInstrumentor, BaseInstrumentorWrapper):

  # Constructor
  def __init__(self):
    logger.debug('Entering RequestsInstrumentorWrapper.__init__().')
    super().__init__()

    def _instrument(self, **kwargs):
        super()._instrument(
            tracer_provider=kwargs.get("tracer_provider"),
            span_callback=kwargs.get("span_callback"),
            name_callback=kwargs.get("name_callback"),
        )

    def _uninstrument(self, **kwargs):
        super()._uninstrument()
