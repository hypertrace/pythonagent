import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from hypertrace.agent.instrumentation.instrumentation_definitions import FAST_API_KEY, _INSTRUMENTATION_STATE
from hypertrace.agent.filter.registry import Registry

def create_instrumented_fast_app(agent):
    if FAST_API_KEY in _INSTRUMENTATION_STATE:
        del _INSTRUMENTATION_STATE[FAST_API_KEY]
    agent._instrument(FAST_API_KEY, auto_instrument=True)
    from fastapi import FastAPI
    app = FastAPI()

    return app


def test_basic_span_data(agent, exporter):
    app = create_instrumented_fast_app(agent)

    @app.post("/")
    async def read_main():
        return {"msg": "Hello World"}

    client = TestClient(app)

    response = client.post("/", json={"key": "value"})
    span_list = exporter.get_finished_spans()
    exporter.clear()
    assert len(span_list) == 1
    span = span_list[0]

    assert span.name == 'POST /'
    attrs = span.attributes
    assert attrs["http.method"] == "POST"
    assert attrs["http.server_name"] == "testserver"
    assert attrs["http.url"] == "http://testserver/"
    assert attrs["http.route"] == "/"

def test_capture_request_data(agent, exporter):
    app = create_instrumented_fast_app(agent)

    @app.post("/some-endpoint")
    async def read_main():
        return {"msg": "Hello World"}

    client = TestClient(app)

    response = client.post("/some-endpoint", json={"key": "value"},
                           headers={"X-Some-Header": "some-value"})
    span_list = exporter.get_finished_spans()
    exporter.clear()
    assert len(span_list) == 1
    span = span_list[0]

    assert span.name == 'POST /some-endpoint'
    attrs = span.attributes
    assert attrs["http.method"] == "POST"
    assert attrs["http.server_name"] == "testserver"
    assert attrs["http.url"] == "http://testserver/some-endpoint"
    assert attrs["http.route"] == "/some-endpoint"
    assert attrs["http.request.header.content-type"] == "application/json"
    assert attrs["http.request.body"] == '{"key": "value"}'
    assert attrs["http.request.header.x-some-header"] == "some-value"

def test_capture_response_data(agent, exporter):
    app = create_instrumented_fast_app(agent)

    @app.get("/return-json")
    async def read_main():
        resp = JSONResponse(content={"msg": "Hello World"})
        return resp

    client = TestClient(app)

    response = client.get("/return-json")
    span_list = exporter.get_finished_spans()
    exporter.clear()
    assert len(span_list) == 1
    span = span_list[0]

    assert span.name == 'GET /return-json'
    attrs = span.attributes
    assert attrs["http.method"] == "GET"
    assert attrs["http.server_name"] == "testserver"
    assert attrs["http.url"] == "http://testserver/return-json"
    assert attrs["http.route"] == "/return-json"
    assert attrs["http.response.header.content-type"] == "application/json"
    assert attrs["http.response.body"] == '{"msg":"Hello World"}'

def test_setup_is_wrapped(agent, exporter):
    app = create_instrumented_fast_app(agent)

    @app.get("/")
    async def read_main():
        return {"msg": "Hello World"}
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

    # since we cant test that its a lambda just test that our function is included in the string signature
    assert str(FastAPI.setup).index('lambda') > 0

def test_headers_can_block(agent_with_filter, exporter):
    app = create_instrumented_fast_app(agent_with_filter)

    @app.get("/block")
    async def read_main():
        return {"msg": "Hello World"}
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/block")
    assert response.status_code == 403

    span_list = exporter.get_finished_spans()
    exporter.clear()
    assert len(span_list) == 1
    span = span_list[0]
    assert span.attributes['http.method'] == 'GET'
    assert span.attributes['http.target'] == '/block'
    assert span.attributes['http.status_code'] == 403

def test_body_can_block(agent_with_body_filter, exporter):
    app = create_instrumented_fast_app(agent_with_body_filter)

    @app.post("/block")
    async def read_main():
        return {"msg": "Hello World"}
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post("/block", json={"key": "value"})
    assert response.status_code == 403

    span_list = exporter.get_finished_spans()
    exporter.clear()
    assert len(span_list) == 1
    span = span_list[0]
    assert span.attributes['http.method'] == 'POST'
    assert span.attributes['http.target'] == '/block'
    assert span.attributes['http.status_code'] == 403


