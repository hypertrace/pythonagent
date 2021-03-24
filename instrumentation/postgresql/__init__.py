import sys
import os.path
import logging
import traceback
from instrumentation import BaseInstrumentorWrapper
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

#Initialize logger with local module name
logger = logging.getLogger(__name__)

# The main entry point 
class PostgreSQLInstrumentorWrapper(Psycopg2Instrumentor, BaseInstrumentorWrapper):

  # Constructor
  def __init__(self):
    logger.debug('Entering PostgreSQLInstrumentorWrapper.__init__().')
    super().__init__()

  def _instrument(self, **kwargs):
    logger.debug('Entering PostgreSQLInstrumentorWrapper._instrument().')
    super()._instrument(**kwargs)

  def _uninstrument(self, **kwargs):
    logger.debug('Entering PostgreSQLInstrumentorWrapper._uninstrument().')
    super()._uninstrument(**kwargs)

  def instrument_connection(self, connection):
    logger.debug('Entering PostgreSQLInstrumentorWrapper.instrument_connection().')
    return super().instrument_connection(connection)

  def uninstrument_connection(self, connection):
    logger.debug('Entering PostgreSQLInstrumentorWrapper.uninstrument_connection().')
    return super().uninstrument_connection(connection)
