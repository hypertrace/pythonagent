import sys
import logging
import traceback
import pytest
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.trace import Span

from hypertrace.agent.filter import Filter
from hypertrace.agent.filter.registry import Registry
from tests.django.testapp.wsgi import TEST_AGENT_INSTANCE


memoryExporter = InMemorySpanExporter()
simpleExportSpanProcessor = SimpleSpanProcessor(memoryExporter)
TEST_AGENT_INSTANCE.register_processor(simpleExportSpanProcessor)

class SampleBlockingFilter(Filter):
    def evaluate_url_and_headers(self, span: Span, url: str, headers: tuple) -> bool:
        return True

    def evaluate_body(self, span: Span, body) -> bool:
        pass

@pytest.mark.django_db
def test_basic_span_data(client):
    response = client.get('/test/123')
    assert response.status_code == 200

    span_list = memoryExporter.get_finished_spans()
    memoryExporter.clear()
    assert len(span_list) == 1
    django_span = span_list[0]
    assert django_span.name == 'GET test/<int:id>'
    attrs = django_span.attributes
    assert attrs["http.method"] == "GET"
    assert attrs["http.server_name"] == "testserver"
    assert attrs["http.url"] == "http://testserver/test/123"
    assert attrs["http.route"] == "test/<int:id>"

@pytest.mark.django_db
def test_collects_body_data(client):
    response = client.post('/test/123', data={"some_client_data": "123"}, content_type="application/json")
    assert response.status_code == 200

    span_list = memoryExporter.get_finished_spans()
    memoryExporter.clear()
    assert len(span_list) == 1
    django_span = span_list[0]
    assert django_span.name == 'POST test/<int:id>'
    attrs = django_span.attributes
    assert attrs["http.request.header.content-type"] == 'application/json'
    assert attrs["http.request.body"] == '{"some_client_data": "123"}'

    assert attrs["http.response.header.content-type"] == 'application/json'
    assert attrs["http.response.body"] == '{"data": 123}'


@pytest.mark.django_db
def test_can_block(client):
    r = Registry()
    r.register(SampleBlockingFilter)
    response = client.post('/test/123', data={"some_client_data": "123"}, content_type="application/json")
    assert response.status_code == 403
    r.filters.clear()
    memoryExporter.clear()


