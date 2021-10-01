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
from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import TracerProvider, export
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from flask import Flask
from hypertrace.agent import Agent

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

server = Flask(__name__)

logger = setup_custom_logger(__name__)

ENABLE_INSTRUMENTATION = bool(os.getenv('ENABLE_INSTRUMENTATION'))

@server.route("/route2")
def testAPI1():
    try:
      logger.info('Serving request for /route2')
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

#@server.teardown_request
def after_request(response):
  try:
    logger.debug("after_request() called")
    if not ENABLE_INSTRUMENTATION:
      return response
    # Get all of the in memory spans that were recorded for this iteration
    span_list = memoryExporter.get_finished_spans()
    # Confirm something was returned.
    assert span_list
    # Confirm there are three spans
    logger.debug('len(span_list): ' + str(len(span_list)))
    assert len(span_list) == 1
    logger.debug('span_list: ' + str(span_list[0].attributes))
    # Convert each span to a JSON object
    flaskSpanAsObject = json.loads(span_list[0].to_json())
    # Flask extended span object attributes should look like:
    #
    # {
    #   "http.method": "GET",
    #   "http.server_name": "localhost",
    #   "http.scheme": "http",
    #   "net.host.port": 5000,
    #   "http.host": "localhost:5000",
    #   "http.target": "/dbtest",
    #   "net.peer.ip": "127.0.0.1",
    #   "http.user_agent": "werkzeug/1.0.1",
    #   "http.flavor": "1.1",
    #   "http.route": "/dbtest",
    #   "http.request.header.user-agent": "werkzeug/1.0.1",
    #   "http.request.header.host": "localhost:5000",
    #   "http.response.header.content-type": "application/json",
    #   "http.response.header.content-length": "26",
    #   "http.response.body": "{ \"a\": \"a\", \"xyz\": \"xyz\" }",
    #   "http.status_text": "OK",
    #   "http.status_code": 200
    # }
    #
    # Dump all attributes for debugging
    for key in flaskSpanAsObject:
      logger.debug(key + ' : ' + str(flaskSpanAsObject[key]))
    # Check that the expected results are in the flask extended span attributes
    assert flaskSpanAsObject['attributes']['http.method'] == 'GET'
    assert flaskSpanAsObject['attributes']['http.target'] == '/route2';
    assert flaskSpanAsObject['attributes']['http.request.header.traceparent']
    assert flaskSpanAsObject['attributes']['http.response.header.content-type'] == 'application/json'
    assert flaskSpanAsObject['attributes']['http.response.body'] == '{ "a": "a", "xyz": "xyz" }'
    assert flaskSpanAsObject['attributes']['http.status_code'] == 200
    memoryExporter.clear()
    return response
  except:
    logger.error('An error occurred validating span data: exception=%s, stacktrace=%s',
      sys.exc_info()[0],
      traceback.format_exc())
    raise sys.exc_info()[0]

agent = None
if ENABLE_INSTRUMENTATION == True:
  #
  # Code snippet here represents the current initialization logic
  #
  logger.info('Initializing agent.')
  agent = Agent()
  agent.instrument(server)
  #
  # End initialization logic for Python Agent
  #
 
  # Setup In-Memory Span Exporter
  logger.info('Agent initialized.')
  logger.info('Adding in-memory span exporter.')
  memoryExporter = InMemorySpanExporter()
  simpleExportSpanProcessor = SimpleSpanProcessor(memoryExporter)
  agent.register_processor(simpleExportSpanProcessor)
  logger.info('Added in-memoy span exporter') 

  # Setup Jaeger Exporter
  logger.info('Adding jaeger span exporter.')
  jaegerExporter = JaegerExporter(
      agent_host_name='localhost',
      agent_port=6831,
  )
  batchExportSpanProcessor = BatchSpanProcessor(jaegerExporter)
  agent.register_processor(batchExportSpanProcessor)
  logger.info('Added jaeger span exporter.')

