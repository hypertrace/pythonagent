import sys
import os
import logging
import traceback
import json
import pytest
import flask
from werkzeug.serving import make_server
from flask import request
import time
import atexit
import threading
import mysql.connector
from flask import Flask
import requests
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor, get_default_span_name
from opentelemetry.sdk.trace import TracerProvider, export
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor

server = Flask(__name__)
FlaskInstrumentor().instrument_app(server)

memoryExporter = InMemorySpanExporter()
simpleExportSpanProcessor = SimpleSpanProcessor(memoryExporter)
tracerProvider = TracerProvider(
  resource=Resource.create({
    'service.name' : 'otel-python-agent',
    'service.instance.id' : os.getpid(),
  })
)

#consoleExporter = ConsoleSpanExporter()
#simpleExportSpanProcessor2 = SimpleSpanProcessor(consoleExporter)

trace.set_tracer_provider(tracerProvider)
trace.get_tracer_provider().add_span_processor(simpleExportSpanProcessor)
#trace.get_tracer_provider().add_span_processor(simpleExportSpanProcessor2)

requestsInstrumentor = RequestsInstrumentor()
requestsInstrumentor.instrument()

def setup_custom_logger(name):
  try:
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('agent.log', mode='a')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger
  except:
    logger.error('Failed to customize logger: exception=%s, stacktrace=%s',
      sys.exc_info()[0],
      traceback.format_exc())

logger = setup_custom_logger(__name__)

@server.route("/dbtest/full-test")
def testAPI1():
    try:
      logger.debug('Serving request for /dbtest/full-test.')
      response = flask.Response(mimetype='application/json')
      response.data = str('{ "a": "a", "xyz": "xyz" }')
      return response
    except:
      logger.error('Failed to initialize postgresql instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      response = flask.Response(mimetype='application/json', status=500)
      response.data = str('{}')
      return response
