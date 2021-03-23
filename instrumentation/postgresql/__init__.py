import sys
import os.path
import logging
import inspect
import flask
import grpc
import json
import traceback
import mysql.connector
from instrumentation import BaseInstrumentorWrapper
from opentelemetry.instrumentation.mysql import MySQLInstrumentor

#Initialize logger with local module name
logger = logging.getLogger(__name__)

# The main entry point 
class PostgreSQLInstrumentorWrapper(MySQLInstrumentor, BaseInstrumentorWrapper):

  # Constructor
  def __init__(self):
    super().__init__()

  def _instrument(self, **kwargs):
    super()._instrument(**kwargs)

  def _uninstrument(self, **kwargs):
    super()._uninstrument(**kwargs)

  def instrument_connection(self, connection):
    return super().instrument_connection(connection)

  def uninstrument_connection(
    self, connection
  ):
    return super().uninstrument_connection(connection)
