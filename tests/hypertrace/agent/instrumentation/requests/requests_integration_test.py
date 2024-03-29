import json

import flask
import requests
# also import this way to test that instrumentation still works
from requests import post
from flask import Flask
from tests import setup_custom_logger
from tests.hypertrace.agent.instrumentation.flask.app import FlaskServer


def test_request_client(agent, exporter):
    try:
        logger = setup_custom_logger(__name__)

        app = Flask(__name__)
        app.use_reloader = False

        @app.route("/route1")
        def api_example():
            response = flask.Response(mimetype='application/json')
            response.headers['tester3'] = 'tester3'
            response.data = str('{ "a": "a", "xyz": "xyz" }')
            return response

        agent.instrument(app)
        server = FlaskServer(app)
        server.start()

        url = f'http://localhost:{server.port}/route1'
        response = requests.get(url)

        spans = exporter.get_finished_spans()
        assert spans
        assert len(spans) == 2
        client_span = json.loads(spans[0].to_json())

        assert client_span['attributes']['http.method'] == 'GET'
        assert client_span['attributes']['http.url'] == f'http://localhost:{server.port}/route1'
        assert client_span['attributes']['http.request.header.accept'] == '*/*'
        assert client_span['attributes'][
                   'http.response.body'] == '{ "a": "a", "xyz": "xyz" }'
        assert client_span['attributes']['http.status_code'] == 200
        assert client_span['attributes']['http.response.header.tester3'] == 'tester3'
        assert client_span['attributes']['http.method'] == 'GET'
    finally:
        server.shutdown()


def test_request_propagation(agent, exporter):
    try:
        logger = setup_custom_logger(__name__)
        logger.info('Initializing flask app.')
        # Create Flask app
        app = Flask(__name__)

        @app.route("/route2")
        def api_example_2():
            headers = {
                'tester1': 'tester1',
                'tester2': 'tester2'
            }
            if flask.request.args.get("a") is None:
                requests.get(url=f'http://localhost:{server.port}/route2?a=foo', headers=headers)
            response = flask.Response(mimetype='application/json')
            response.headers['tester3'] = 'tester3'
            response.data = str('{ "a": "a", "xyz": "xyz" }')
            return response

        agent.instrument(app)
        server = FlaskServer(app)
        server.start()

        logger.info('Agent initialized.')

        r1 = app.test_client().get(f'http://localhost:{server.port}/route2',
                                   headers={'tester1': 'tester1', 'tester2': 'tester2'})
        # Get all of the in memory spans that were recorded for this iteration

        spans = exporter.get_finished_spans()
        # Confirm something was returned.
        assert spans
        # 3 spans => server => requests => server
        assert len(spans) == 3
        server_2_span = json.loads(spans[0].to_json())
        request_span = json.loads(spans[1].to_json())
        server_1_span = json.loads(spans[2].to_json())
        # Check that the expected results are in the flask extended span attributes
        assert server_1_span['attributes']['http.method'] == 'GET'
        assert server_1_span['attributes']['http.route'] == '/route2'
        assert server_1_span['attributes']['http.response.header.content-type'] == 'application/json'
        assert server_1_span['attributes'][
                   'http.response.body'] == '{ "a": "a", "xyz": "xyz" }'
        assert server_1_span['attributes']['http.status_code'] == 200
        assert server_1_span['attributes']['http.response.header.tester3'] == 'tester3'

        assert request_span["kind"] == "SpanKind.CLIENT"
        assert request_span['attributes']['http.method'] == 'GET'
        assert request_span['attributes']['http.url'] == f'http://localhost:{server.port}/route2?a=foo'
        assert request_span['attributes']['http.status_code'] == 200

        assert server_2_span["kind"] == "SpanKind.SERVER"
        assert server_2_span['attributes']['http.request.header.traceparent']
        assert server_2_span['attributes']['http.method'] == 'GET'
        assert server_2_span['attributes']['http.url'] == f'http://localhost:{server.port}/route2?a=foo'
        assert server_2_span['attributes']['http.status_code'] == 200
        exporter.clear()
        a1 = r1.get_json()['a']
        assert a1 == 'a'
    finally:
        server.shutdown()

def test_request_client_imported(agent, exporter):
    try:
        logger = setup_custom_logger(__name__)

        app = Flask(__name__)
        app.use_reloader = False

        @app.route("/route1", methods=["GET", "POST"])
        def api_example():
            response = flask.Response(mimetype='application/json')
            response.headers['tester3'] = 'tester3'
            response.data = str('{ "a": "a", "xyz": "xyz" }')
            return response

        agent.instrument(app)
        server = FlaskServer(app)
        server.start()

        url = f'http://localhost:{server.port}/route1'
        response = post(url, json={"test": "body"})

        spans = exporter.get_finished_spans()
        assert spans
        assert len(spans) == 2
        client_span = json.loads(spans[1].to_json())

        assert client_span['kind'] == "SpanKind.CLIENT"
        assert client_span['attributes']['http.method'] == 'POST'
        assert client_span['attributes']['http.url'] == f'http://localhost:{server.port}/route1'
        assert client_span['attributes']['http.request.header.accept'] == '*/*'
        assert client_span['attributes']['http.request.header.content-type'] == 'application/json'
        assert client_span['attributes']['http.request.body'] == '{"test": "body"}'
        assert client_span['attributes'][
                   'http.response.body'] == '{ "a": "a", "xyz": "xyz" }'
        assert client_span['attributes']['http.status_code'] == 200
        assert client_span['attributes']['http.response.header.tester3'] == 'tester3'
    finally:
        server.shutdown()

def test_invalid_unicode_character(agent, exporter):
    try:
        logger = setup_custom_logger(__name__)

        app = Flask(__name__)
        app.use_reloader = False

        @app.route("/invalidutf8", methods=["GET", "POST"])
        def api_example():
            response = flask.Response(mimetype='application/json')
            response.headers['tester3'] = 'tester3'
            response.data = str('{ "a": "a", "xyz": "xyz" }')
            return response

        agent.instrument(app)
        server = FlaskServer(app)
        server.start()

        url = f'http://localhost:{server.port}/invalidutf8'
        response = post(url, data={"test": b"This is some text with an invalid byte: \x9c"})

        spans = exporter.get_finished_spans()
        assert spans
        assert len(spans) == 2
        client_span = json.loads(spans[1].to_json())

        assert client_span['kind'] == "SpanKind.CLIENT"
        assert client_span['attributes']['http.method'] == 'POST'
        assert client_span['attributes']['http.url'] == f'http://localhost:{server.port}/invalidutf8'
        assert client_span['attributes']['http.request.header.accept'] == '*/*'
        assert client_span['attributes']['http.request.header.content-type'] == 'application/x-www-form-urlencoded'
        assert client_span['attributes']['http.request.body'] == 'test=This+is+some+text+with+an+invalid+byte%3A+%9C'
        assert client_span['attributes'][
                   'http.response.body'] == '{ "a": "a", "xyz": "xyz" }'
        assert client_span['attributes']['http.status_code'] == 200
        assert client_span['attributes']['http.response.header.tester3'] == 'tester3'
    finally:
        server.shutdown()