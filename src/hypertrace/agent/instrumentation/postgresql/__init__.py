'''Hypertrace wrapper around OTel postgresql instrumentor'''
import sys
import os.path
import logging
import traceback
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from hypertrace.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__) # pylint: disable=C0103

class PostgreSQLInstrumentorWrapper(Psycopg2Instrumentor, BaseInstrumentorWrapper):
    '''Hypertrace wrapper around OTel postgresql instrumentor class'''
