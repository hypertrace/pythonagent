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

Initialize logger with local module name
logger = logging.getLogger(__name__)

# The main entry point 
class MySqlInstrumentorWrapper(MySQLInstrumentor, BaseInstrumentorWrapper):
  def __init__(self):
    super().__init__(self)

  def _instrument(self, **kwargs):
    super()._instrument(**kwargs)
#    tracer_provider = kwargs.get("tracer_provider")
#    dbapi.wrap_connect(
#      __name__,
#      mysql.connector,
#      "connect",
#      self._DATABASE_SYSTEM,
#      self._CONNECTION_ATTRIBUTES,
#      version=__version__,
#      tracer_provider=tracer_provider,
#    )

  def _uninstrument(self, **kwargs):
    super()._uninstrument(**kwargs)
#    dbapi.unwrap_connect(mysql.connector, "connect")

  # pylint:disable=no-self-use
  def instrument_connection(self, connection):
    super().instrument_connection(connection)
#    tracer = get_tracer(__name__, __version__)
#    return dbapi.instrument_connection(
#      tracer,
#      connection,
#      self._DATABASE_SYSTEM,
#      self._CONNECTION_ATTRIBUTES,
#    )

    def uninstrument_connection(self, connection):
      return super().uninstrument_connection(connecion)
#      return dbapi.uninstrument_connection(connection)
