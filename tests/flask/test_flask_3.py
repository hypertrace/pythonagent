import sys
import logging
import flask
import traceback
import json
from werkzeug.serving import make_server
from flask import request, Flask
import threading
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

@app.route('/test/postdata', methods=['POST'])
def post_api():
    data = request.get_json()
    logger.info('Serving request for /test/postdata')
    response = flask.Response(mimetype='application/json')
    response.headers['tester3'] = 'tester3'
    sum1 = data['d1'] ;
    sum2 = data['d2'] ;
    response.data = str(sum1+sum2)
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

def test_run():
  logger.info('Running test calls.')
  with app.test_client() as c:
    try:
        logger.info('Making test call to /test/postdata')
        r3 = app.test_client().post('http://localhost:5000/test/postdata',
        headers={'tester1': 'tester1', 'tester2': 'tester2'},
        data=json.dumps({'d1': 10, 'd2': 20}), content_type='application/json')
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
        assert flaskSpanAsObject['attributes']['http.method'] == 'POST'
        assert flaskSpanAsObject['attributes']['http.target'] == '/test/postdata'
        assert flaskSpanAsObject['attributes']['http.request.body'] == '{"d1": 10, "d2": 20}'
        assert flaskSpanAsObject['attributes']['http.request.header.tester1'] == 'tester1'
        assert flaskSpanAsObject['attributes']['http.request.header.tester2'] == 'tester2'
        assert flaskSpanAsObject['attributes']['http.response.header.content-type'] == 'application/json'
        assert flaskSpanAsObject['attributes']['http.response.body'] == '30'
        assert flaskSpanAsObject['attributes']['http.status_code'] == 200
        assert flaskSpanAsObject['attributes']['http.response.header.tester3'] == 'tester3'
        memoryExporter.clear()
        logger.info('Reading /test/postdata response')
        a3 = r3.status_code
        assert a3 == 200
        logger.info('r3 result: ' + str(a3))
        logger.info('Exiting from flask instrumentation test.')
        return 0
    except:
      logger.error('Failed to initialize flask instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]
