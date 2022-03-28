import sys
import flask
import traceback
from flask import Flask
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from hypertrace.agent import Agent

# Run the flask web server in a separate thread
from tests import setup_custom_logger
from tests.hypertrace.agent.instrumentation.flask.app import FlaskServer


def test_run(agent, exporter):
    logger = setup_custom_logger(__name__)
    logger.info('Initializing flask app.')
    # Create Flask app
    app = Flask(__name__)

    @app.route("/route1")
    def api_1():
        logger.info('Serving request for /route1.')
        response = flask.Response(mimetype='application/json')
        response.headers['tester3'] = 'tester3'
        response.data = str('{ "a": "a", "xyz": "xyz" }')
        return response

    @app.route("/route2")
    def api_2():
        logger.info('Serving request for /route2.')
        response = flask.Response(mimetype='application/json')
        response.headers['tester3'] = 'tester3'
        response.data = str('{ "a": "a", "xyz": "xyz" }')
        return response

    agent.instrument(app)

    server = FlaskServer(app)
    server.start()

    logger.info('Running test calls.')
    with app.test_client() as c:
        logger.info('Making test call to /route1')
        r1 = app.test_client().get('http://localhost:5000/route1', headers={'tester1': 'tester1', 'tester2': 'tester2'})
        logger.info('Making test call to /route2')
        r2 = app.test_client().get('http://localhost:5000/route2', headers={'tester1': 'tester1', 'tester2': 'tester2'})

        logger.info('Reading /route1 response.')
        a1 = r1.get_json()['a']
        logger.info('Reading /route2 response.')
        a2 = r2.get_json()['a']
        assert a1 == 'a'
        assert a2 == 'a'
        logger.info('r1 result: ' + str(a1))
        logger.info('r2 result: ' + str(a2))
        logger.info('Exiting from flask instrumentation test.')
        server.shutdown()