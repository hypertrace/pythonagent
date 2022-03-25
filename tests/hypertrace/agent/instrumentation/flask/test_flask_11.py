import sys
import logging
import flask
import traceback
import json
from werkzeug.serving import make_server
import threading
from flask import Flask, send_file


# Run the flask web server in a separate thread
from tests import setup_custom_logger


def test_run(agent, exporter):
    logger = setup_custom_logger(__name__)
    logger.info('Initializing flask app.')
    # Create Flask app
    app = Flask(__name__)

    @app.route("/route1")
    def api_1():
        logger.info('Serving request for /route1.')
        return send_file("./app.py")

    @app.route("/unicode")
    def api_2():
        response = flask.Response(mimetype='application/x-www-form-urlencoded')
        response.data = b'\x80abc'
        return response

    agent.instrument(app)
    logger.info('Agent initialized.')

    logger.info('Running test calls.')
    with app.test_client() as c:
        logger.info('Making test call to /route1')
        r1 = app.test_client().get('http://localhost:5000/route1',
                                   headers={'tester1': 'tester1', 'tester2': 'tester2'})

        assert r1.status_code == 200
        span_list = exporter.get_finished_spans()
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

        exporter.clear()

        r2 = app.test_client().get('http://localhost:5000/unicode')
        assert r2.status_code == 200
        span_list = exporter.get_finished_spans()
        assert span_list
        assert len(span_list) == 1
        flaskSpanAsObject = json.loads(span_list[0].to_json())

        # Check that the expected results are in the flask extended span attributes
        assert flaskSpanAsObject['attributes']['http.method'] == 'GET'
        assert flaskSpanAsObject['attributes']['http.target'] == '/unicode'
        assert flaskSpanAsObject['attributes']['http.response.body'] == "\\x80abc"
