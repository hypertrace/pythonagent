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
from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import TracerProvider, export
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from agent import Agent
from flask import Flask

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

def databaseTest():
  try:
    logger.info('Making connection to mysql.')
    cnx = mysql.connector.connect(database='hypertrace',
      user='root',
      password='example',
      host='db',
      port=3306)
    logger.info('Connect successfully.')
    cursor = cnx.cursor()
    logger.info('Running INSERT statement.')
    cursor.execute("INSERT INTO hypertrace_data (col1, col2) VALUES (123, 'abcdefghijklmnopqrstuvwxyz')")
    logger.info('Statement ran successfully')
    logger.info('Closing cursor.')
    cursor.close()
    logger.info('Closing connection.')
    cnx.close()
    logger.info('Connection closed.')
  except:
    logger.error('Failed to initialize postgresql instrumentation wrapper: exception=%s, stacktrace=%s',
      sys.exc_info()[0],
      traceback.format_exc())
    raise sys.exc_info()[0]

@server.route("/dbtest/full-test")
def testAPI1():
    try:
      logger.info('Serving request for /dbtest/full-test.')
      databaseTest() 
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
    assert len(span_list) == 2
    logger.debug('span_list: ' + str(span_list[1].attributes))
    logger.debug('span_list: ' + str(span_list[0].attributes))
    # Convert each span to a JSON object
    flaskSpanAsObject = json.loads(span_list[1].to_json())
    sql1SpanAsObject = json.loads(span_list[0].to_json())
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
    assert flaskSpanAsObject['attributes']['http.target'] == '/dbtest/full-test' or flaskSpanAsObject['attributes']['http.target'] == '/dbtest/no-confirmation' or flaskSpanAsObject['attributes']['http.target'] == '/dbtest/no-hypertrace'
    assert flaskSpanAsObject['attributes']['http.response.header.content-type'] == 'application/json'
    assert flaskSpanAsObject['attributes']['http.response.body'] == '{ "a": "a", "xyz": "xyz" }'
    assert flaskSpanAsObject['attributes']['http.status_code'] == 200
    # MySQL INSERT Extended span Object
    # {
    #   "db.system": "mysql",
    #   "db.name": "hypertrace",
    #   "db.statement": "INSERT INTO hypertrace_data (col1, col2) VALUES (123, \"abcdefghijklmnopqrstuvwxyz\")",
    #   "db.user": "root",
    #   "net.peer.name": "localhost",
    #   "net.peer.port": 3306
    # }
    for key in sql1SpanAsObject:
      logger.debug(key + ' : ' + str(sql1SpanAsObject[key]))
    assert sql1SpanAsObject['attributes']['db.system'] == 'mysql'
    assert sql1SpanAsObject['attributes']['db.name'] == 'hypertrace'
    assert sql1SpanAsObject['attributes']['db.user'] == 'root'
    assert sql1SpanAsObject['attributes']['net.peer.name'] == 'db'
    assert sql1SpanAsObject['attributes']['net.peer.port'] == 3306
    assert sql1SpanAsObject['attributes']['db.statement'] == "INSERT INTO hypertrace_data (col1, col2) VALUES (123, 'abcdefghijklmnopqrstuvwxyz')"
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
  agent.registerFlaskApp(server)
  agent.registerMySQL()
  #
  # End initialization logic for Python Agent
  #
 
  # Setup In-Memory Span Exporter
  logger.info('Agent initialized.')
  logger.info('Adding in-memory span exporter.')
  memoryExporter = InMemorySpanExporter()
  simpleExportSpanProcessor = SimpleSpanProcessor(memoryExporter)
  agent.setProcessor(simpleExportSpanProcessor)
  logger.info('Added in-memoy span exporter') 
