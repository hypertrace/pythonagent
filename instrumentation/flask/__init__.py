import sys
import os.path
import logging
from opentelemetry.instrumentation.flask import FlaskInstrumentor
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from instrumentation import BaseInstrumentorWrapper

class FlaskInstrumentorWrapper(FlaskInstrumentor, BaseInstrumentorWrapper):
  def __init__(self):
    logging.debug('Entering FlaskInstrumentorWrapper constructor.');
    super().__init__() 

  def instrument_app(self, app):
    logging.debug('Entering FlaskInstrumentorWrapper.instument_app().')
    super().instrument_app(app)
