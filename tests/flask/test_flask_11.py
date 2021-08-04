import sys
import logging
import flask
import traceback
import json
from werkzeug.serving import make_server
import threading
from flask import Flask, send_file
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
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


# @pytest.mark.serial
def test_run():
    logger = setup_custom_logger(__name__)
    logger.info('Initializing flask app.')
    # Create Flask app
    app = Flask(__name__)

    @app.before_first_request
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
        return send_file("./tox.ini")

    @app.route("/unicode")
    def testAPI2():
        response = flask.Response(mimetype='application/x-www-form-urlencoded')
        response.data = b'\x80abc'
        return response

    @app.route("/terminate")
    def terminate():
        logger.info('Serving request for /terminatae.')
        shutdown_server()
        response = flask.Response()
        response.data = {'a': 'a', 'xyz': 'xyz'}
        return response

    logger.info('Flask app initialized.')

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

    server = FlaskServer(app)

    # Setup In-Memory Span Exporter
    logger.info('Agent initialized.')
    logger.info('Adding in-memory span exporter.')
    memoryExporter = InMemorySpanExporter()
    simpleExportSpanProcessor = SimpleSpanProcessor(memoryExporter)
    agent.register_processor(simpleExportSpanProcessor)
    logger.info('Added in-memory span exporter')

    logger.info('Running test calls.')
    with app.test_client() as c:
        try:
            logger.info('Making test call to /route1')
            r1 = app.test_client().get('http://localhost:5000/route1',
                                        headers={'tester1': 'tester1', 'tester2': 'tester2'})

            assert r1.status_code == 200
            span_list = memoryExporter.get_finished_spans()
            assert span_list
            assert len(span_list) == 1
            flaskSpanAsObject = json.loads(span_list[0].to_json())

            # Check that the expected results are in the flask extended span attributes
            assert flaskSpanAsObject['attributes']['http.method'] == 'GET'
            assert flaskSpanAsObject['attributes']['http.target'] == '/route1'
            assert flaskSpanAsObject['attributes']['http.status_code'] == 200
            body_message = ""
            try:
                 body_message = flaskSpanAsObject['attributes']['http.response.body']
            except KeyError:
                body_message = "key does not exist"
                print("key does not exist")

            assert body_message == "key does not exist"

            memoryExporter.clear()

            r2 = app.test_client().get('http://localhost:5000/unicode')
            assert r2.status_code == 200
            span_list = memoryExporter.get_finished_spans()
            assert span_list
            assert len(span_list) == 1
            flaskSpanAsObject = json.loads(span_list[0].to_json())

            # Check that the expected results are in the flask extended span attributes
            assert flaskSpanAsObject['attributes']['http.method'] == 'GET'
            assert flaskSpanAsObject['attributes']['http.target'] == '/unicode'
            assert flaskSpanAsObject['attributes']['http.response.body'] == "\\x80abc"
            return 0
        except:
            logger.error('Failed to initialize flask instrumentation wrapper: exception=%s, stacktrace=%s',
                         sys.exc_info()[0],
                         traceback.format_exc())
            raise sys.exc_info()[0]
