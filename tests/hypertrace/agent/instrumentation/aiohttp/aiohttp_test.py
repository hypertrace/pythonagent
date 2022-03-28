import flask
import pytest
import json
import aiohttp
from flask import Flask

from tests import setup_custom_logger
from tests.hypertrace.agent.instrumentation.flask.app import FlaskServer


@pytest.mark.asyncio
async def test_aiohttp_post(agent, exporter):
    logger = setup_custom_logger(__name__)
    app = Flask(__name__)
    app.use_reloader = False

    @app.route("/route1", methods=["POST"])
    def api_example():
        response = flask.Response(mimetype='application/json')
        response.headers['tester3'] = 'tester3'
        response.data = str('{ "a": "a", "xyz": "xyz" }')
        return response

    server = FlaskServer(app)
    server.start()
    agent.instrument(app)

    # Make test call
    async with aiohttp.ClientSession() as session:
        async with session.post(f'http://localhost:{server.port}/route1', data='{ "a":"b", "c": "d" }',
                                headers={'tester1': 'tester1', 'tester2': 'tester2'}) as response:
            response_body = await response.json()
            logger.info('Received: %s', str(response_body))
            a = response_body['a']
            assert a == 'a'
            span_list = exporter.get_finished_spans()

            assert span_list

            assert len(span_list) == 3
            aiohttpSpanAsObject = json.loads(span_list[0].to_json())

            assert aiohttpSpanAsObject['attributes']['http.method'] == 'POST'
            assert aiohttpSpanAsObject['attributes']['http.url'] == f'http://localhost:{server.port}/route1'
            assert aiohttpSpanAsObject['attributes']['http.request.header.tester1'] == 'tester1'
            assert aiohttpSpanAsObject['attributes']['http.request.header.tester2'] == 'tester2'
            assert aiohttpSpanAsObject['attributes']['http.response.header.content-type'] == 'application/json'
            assert aiohttpSpanAsObject['attributes']['http.response.body'] == '{ "a": "a", "xyz": "xyz" }'

            assert aiohttpSpanAsObject['attributes']['http.status_code'] == 200
            server.shutdown()