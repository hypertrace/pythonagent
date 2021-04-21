import sys
import os
import logging
import flask
import pytest
import traceback
import json
import pytest
from werkzeug.serving import make_server
from flask import request, Flask
import time
import atexit
import threading
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

logger = setup_custom_logger(__name__)

logger.info('Initializing flask app.')
# Create Flask app
app = Flask(__name__)
logger.info('Flask app initialized.')

def before_first_request():
  logger.debug("test_program: before_first_request() called")

@app.before_request
def before_request():
    logger.debug("test_progam: before_request() called")

@app.after_request
def after_request(response):
    logger.debug("test_program: after_request() called")
    return response

@app.route("/route1")
def testAPI1():
  logger.info('Serving request for /route1.')
  response = flask.Response(mimetype='application/graphql')
  response.headers['tester3'] = 'tester3'
  response.data = str('''{
  "errors": [
    {
      "message": "Name for character with ID 1002 could not be fetched.",
      "locations": [ { "line": 6, "column": 7 } ],
      "path": [ "hero", "heroFriends", 1, "name" ]
    }
  ],
  "data": {
    "hero": {
      "name": "R2-D2",
      "heroFriends": [
        {
          "id": "1000",
          "name": "Luke Skywalker"
        },
        {
          "id": "1002",
          "name": null
        },
        {
          "id": "1003",
          "name": "Leia Organa"
        }
      ]
    }
  }
}''').replace('\n','')
  return response

# Run the flask web server in a separate thread
class FlaskServer(threading.Thread):
  def __init__(self, app):
    super().__init__()
    self.daemon = True
    threading.Thread.__init__(self)
    self.srv = make_server('localhost', 5000, app)
    self.ctx = app.app_context()
    self.ctx.push()

  def run(self):
    logger.info('starting server.')
    self.srv.serve_forever()
    self.start()

  def shutdown(self):
    logger.info('Shutting down server.')
    self.srv.shutdown()

server = FlaskServer(app)

#
# Code snippet here represents the current initialization logic
#
logger.info('Initializing agent.')
agent = Agent()
agent.register_flask_app(app)
#
# End initialization logic for Python Agent
#
logger.info('Agent initialized.')

# Setup In-Memory Span Exporter
logger.info('Agent initialized.')
logger.info('Adding in-memory span exporter.')
memoryExporter = InMemorySpanExporter()
simpleExportSpanProcessor = SimpleSpanProcessor(memoryExporter)
agent.register_processor(simpleExportSpanProcessor)

logger.info('Added in-memoy span exporter')

@pytest.mark.serial
def test_run():
  logger.info('Running test calls.')
  with app.test_client():
    try: 
      logger.info('Making test call to /route1')
      r1 = app.test_client().get('http://localhost:5000/route1', headers={ 'tester1': 'tester1', 'tester2':'tester2'})
      # Get all of the in memory spans that were recorded for this iteration
      span_list = memoryExporter.get_finished_spans()
      # Confirm something was returned.
      assert span_list
      # Confirm there are three spans
      logger.debug('len(span_list): ' + str(len(span_list)))
      assert len(span_list) == 1
      logger.debug('span_list: ' + str(span_list[0].attributes))
      flaskSpanAsObject = json.loads(span_list[0].to_json())
      # Check that the expected results are in the flask extended span attributes
      assert flaskSpanAsObject['attributes']['http.method'] == 'GET'
      assert flaskSpanAsObject['attributes']['http.target'] == '/route1'
      assert flaskSpanAsObject['attributes']['http.request.header.tester1'] == 'tester1'
      assert flaskSpanAsObject['attributes']['http.request.header.tester2'] == 'tester2'
      assert flaskSpanAsObject['attributes']['http.response.header.content-type'] == 'application/graphql'
      assert 'R2-D2' in flaskSpanAsObject['attributes']['http.response.body']
      assert flaskSpanAsObject['attributes']['http.status_code'] == 200
      assert flaskSpanAsObject['attributes']['http.response.header.tester3'] == 'tester3'
      memoryExporter.clear()
      a1 = json.loads(r1.data.decode('UTF8'))['data']['hero']['name']
      logger.info('Reading /route1 response: ' + str(a1))
      assert a1 == 'R2-D2'
      logger.info('r1 result: ' + str(a1))
      logger.info('Exiting from flask instrumentation test.')
    except:
      logger.error('Failed to initialize mysql instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]