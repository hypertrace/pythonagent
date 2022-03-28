import sys
import os
import logging
import flask
import pytest
import traceback
import json

from opentelemetry.trace import Span
from werkzeug.serving import make_server
from flask import request
import time
import atexit
import threading
from flask import Flask
# from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import TracerProvider, export
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from hypertrace.agent import Agent
from hypertrace.agent.filter import Filter
from hypertrace.agent.filter.registry import Registry
from tests import setup_custom_logger
from tests.hypertrace.agent.instrumentation.flask.app import FlaskServer


# @pytest.mark.serial
def test_run(agent_with_filter, exporter):
    logger = setup_custom_logger(__name__)

    app = Flask(__name__)

    @app.route("/route1")
    def api_1():
        logger.info('Serving request for /route1.')
        response = flask.Response(mimetype='application/json')
        response.headers['tester3'] = 'tester3'
        response.data = str('{ "a": "a", "xyz": "xyz" }')
        return response

    agent_with_filter.instrument(app)

    server = FlaskServer(app)

    logger.info('Running test calls.')
    with app.test_client() as c:
        logger.info('Making test call to /route1')
        r1 = app.test_client().get('http://localhost:5000/route1',
                                   headers={'tester1': 'tester1', 'tester2': 'tester2'})

        assert r1.status_code == 403
        span_list = exporter.get_finished_spans()
        assert span_list
        assert len(span_list) == 1
        flaskSpanAsObject = json.loads(span_list[0].to_json())

        # Check that the expected results are in the flask extended span attributes
        assert flaskSpanAsObject['attributes']['http.method'] == 'GET'
        assert flaskSpanAsObject['attributes']['http.target'] == '/route1'
        assert flaskSpanAsObject['attributes']['http.status_code'] == 403
