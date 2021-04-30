import sys
import os
import logging
import flask
import pytest
import traceback
import json
import requests
from werkzeug.serving import make_server
from flask import request
import time
import atexit
import threading
from flask import Flask
from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import TracerProvider, export
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
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
    print('Failed to customize logger: exception=%s, stacktrace=%s',
      sys.exc_info()[0],
      traceback.format_exc())

# Run the flask web server in a separate thread
class FlaskServer(threading.Thread):
  def __init__(self, app, port):
    super().__init__()
    self.daemon = True
    threading.Thread.__init__(self)
    self.srv = make_server('localhost', port, app, threaded=True)
    self.ctx = app.app_context()
    self.ctx.push()

  def run(self):
    logger.info('starting server.')
    self.srv.serve_forever()
    self.start()

  def shutdown(self):
    logger.info('Shutting down server.')
    self.srv.shutdown()

def test_run():
  logger = setup_custom_logger(__name__)
  logger.info('Initializing flask app.')
  # Create Flask app
  app1 = Flask(__name__ + '1')

  @app1.route("/route1")
  def testAPI1():
    logger.info('Serving request for /route1.')
    #Make test call
    logger.info('Making call to /route2.')
    headers = { 
      'tester1': 'tester1',
      'tester2': 'tester2'
    }
    response = requests.get(url='http://localhost:8000/route2', headers=headers)
    logger.info('response: ' + str(response))
    response = flask.Response(mimetype='application/json')
    response.headers['tester3'] = 'tester3'
    response.data = str('{ "a": "a", "xyz": "xyz" }')
    return response

  #
  # Code snippet here represents the current initialization logic
  #
  logger.info('Initializing agent.')
  agent = Agent()
  agent.register_flask_app(app1)
  agent.register_requests()
  #
  # End initialization logic for Python Agent
  #
  logger.info('Agent initialized.')

  server1 = FlaskServer(app1, 5000)
  # Setup In-Memory Span Exporter
  logger.info('Agent initialized.')
  logger.info('Adding in-memory span exporter.')
  memoryExporter = InMemorySpanExporter()
  simpleExportSpanProcessor = SimpleSpanProcessor(memoryExporter)
  agent.register_processor(simpleExportSpanProcessor)
  logger.info('Added in-memoy span exporter')

  logger.info('Running test calls.')
  with app1.test_client() as c:
    try:
      logger.info('Making test call to /route1')
      r1 = app1.test_client().get('http://localhost:5000/route1', headers={ 'tester1': 'tester1', 'tester2':'tester2'})
      # Get all of the in memory spans that were recorded for this iteration
      span_list = memoryExporter.get_finished_spans()
      # Confirm something was returned.
      assert span_list
      # Confirm there are two spans
      logger.debug('len(span_list): ' + str(len(span_list)))
      assert len(span_list) == 2
      logger.debug('span_list: ' + str(span_list[1].attributes))
      logger.debug('span_list: ' + str(span_list[0].attributes))
      flaskSpanAsObject = json.loads(span_list[1].to_json())
      requestsSpanAsObject = json.loads(span_list[0].to_json())
      # Check that the expected results are in the flask extended span attributes
      assert flaskSpanAsObject['attributes']['http.method'] == 'GET'
      assert flaskSpanAsObject['attributes']['http.target'] == '/route1'
      assert flaskSpanAsObject['attributes']['http.request.header.tester1'] == 'tester1'
      assert flaskSpanAsObject['attributes']['http.request.header.tester2'] == 'tester2'
      assert flaskSpanAsObject['attributes']['http.response.header.content-type'] == 'application/json'
      assert flaskSpanAsObject['attributes']['http.response.body'] == '{ "a": "a", "xyz": "xyz" }'
      assert flaskSpanAsObject['attributes']['http.status_code'] == 200
      assert flaskSpanAsObject['attributes']['http.response.header.tester3'] == 'tester3'
      logger.info('requestsSpanAsObject: ' + json.dumps(requestsSpanAsObject))
      memoryExporter.clear()
      logger.info('Reading /route1 response.')
      a1 = r1.get_json()['a']
      assert a1 == 'a'
      logger.info('r1 result: ' + str(a1))
      logger.info('Exiting from flask instrumentation test.')
      return 0
    except:
      logger.error('Failed to initialize requests + flask instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]
