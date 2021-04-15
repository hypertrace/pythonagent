import sys
import os.path
import logging
import inspect
import flask
import grpc
import json
import traceback
import mysql.connector
from opentelemetry.instrumentation.mysql import MySQLInstrumentor
from hypertrace.agent.instrumentation import BaseInstrumentorWrapper

#Initialize logger with local module name
logger = logging.getLogger(__name__)

# The main entry point 
class MySQLInstrumentorWrapper(MySQLInstrumentor, BaseInstrumentorWrapper):

  # Constructor
  def __init__(self):
    super().__init__()

  # Overload, but still invoke, parent method
  def _instrument(self, **kwargs):
    super()._instrument(**kwargs)

  # Overload, but still invoke, parent method
  def _uninstrument(self, **kwargs):
    super()._uninstrument(**kwargs)

  # Overload, but still invoke, parent method
  def instrument_connection(self, connection):
    super().instrument_connection(connection)

  # Overload, but still invoke, parent method
  def uninstrument_connection(self, connection):
      return super().uninstrument_connection(connecion)
