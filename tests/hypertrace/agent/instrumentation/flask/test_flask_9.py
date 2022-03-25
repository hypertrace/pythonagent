import sys
import flask
import traceback
import json
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

    @app.route("/route1", methods=['GET'])
    def api_1():
        logger.info('Serving request for /route1.')
        response = flask.Response(mimetype='application/json')
        response.headers['tester3'] = 'tester3'
        response.data = str('{ "a": "a", "xyz": "xyz" }')
        return response

    @app.route("/route2", methods=['GET'])
    def api_2():
        logger.info('Serving request for /route2.')
        response = flask.Response(mimetype='application/json')
        response.headers['tester3'] = 'tester3'
        response.data = str('{ "a": "a", "xyz": "xyz" }')
        return response

    @app.route('/home/<name>', methods=['GET'])
    def api_3(name):
        logger.info('Serving request for /home.')
        return "hello," + name

    agent.instrument(app)

    server = FlaskServer(app)
    server.start()

    with app.test_client() as c:
        logger.info('Making test call to /route1')
        r1 = app.test_client().get('http://localhost:5000/route1',
                                   headers={'tester1': 'tester1', 'tester2': 'tester2'})
        # Get all of the in memory spans that were recorded for this iteration
        span_list = exporter.get_finished_spans()
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
        assert flaskSpanAsObject['attributes']['http.response.header.content-type'] == 'application/json'
        assert flaskSpanAsObject['attributes']['http.response.body'] == '{ "a": "a", "xyz": "xyz" }'
        assert flaskSpanAsObject['attributes']['http.status_code'] == 200
        assert flaskSpanAsObject['attributes']['http.response.header.tester3'] == 'tester3'
        exporter.clear()

        logger.info('Making test call to /route2')
        r2 = app.test_client().get('http://localhost:5000/route2',
                                   headers={'tester1': 'tester1', 'tester2': 'tester2'})
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
        assert flaskSpanAsObject['attributes']['http.response.header.content-type'] == 'application/json'
        assert flaskSpanAsObject['attributes']['http.response.body'] == '{ "a": "a", "xyz": "xyz" }'
        assert flaskSpanAsObject['attributes']['http.status_code'] == 200
        assert flaskSpanAsObject['attributes']['http.response.header.tester3'] == 'tester3'
        exporter.clear()

        logger.info('Making test call to /home')
        r3 = app.test_client().get('http://localhost:5000/home/test')
        span_list = exporter.get_finished_spans()
        # Confirm something was returned.
        assert span_list
        # Confirm there are three spans
        logger.debug('len(span_list): ' + str(len(span_list)))
        assert len(span_list) == 1
        logger.debug('span_list: ' + str(span_list[0].attributes))
        flaskSpanAsObject = json.loads(span_list[0].to_json())
        # Check that the expected results are in the flask extended span attributes
        assert flaskSpanAsObject['attributes']['http.method'] == 'GET'
        assert flaskSpanAsObject['attributes']['http.target'] == '/home/test'
        assert flaskSpanAsObject['attributes']['http.status_code'] == 200
        assert flaskSpanAsObject['name'] == 'GET /home/<name>'

        exporter.clear()

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