import os

import pytest
from pytest_django.lazy_django import skip_if_no_django

from hypertrace.agent.instrumentation.instrumentation_definitions import DJANGO_KEY, _INSTRUMENTATION_STATE
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.trace import Span

from hypertrace.agent.filter import Filter
from hypertrace.agent.filter.registry import Registry
from tests.hypertrace.agent.instrumentation.django.testapp.wsgi import TEST_AGENT_INSTANCE

memoryExporter = InMemorySpanExporter()
simpleExportSpanProcessor = SimpleSpanProcessor(memoryExporter)
TEST_AGENT_INSTANCE.register_processor(simpleExportSpanProcessor)

class SampleBlockingFilter(Filter):
    def evaluate_url_and_headers(self, span: Span, url: str, headers: dict, request_type) -> bool:
        return True

    def evaluate_body(self, span: Span, body, headers: dict, request_type) -> bool:
        pass

# flask & django client fixtures conflict
# this is just a copy paste of the django client fixture so we can explicitly specify it
@pytest.fixture()
def django_client() -> "django.test.client.Client":
    """A Django test client instance."""
    skip_if_no_django()

    from django.test.client import Client

    return Client()

@pytest.fixture(autouse=True)
def clear_instance():
    memoryExporter.clear()
    yield
    memoryExporter.clear()


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.hypertrace.agent.instrumentation.django.testapp.settings')
def test_basic_span_data(django_client):
    response = django_client.get('/test/123')
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

def test_collects_body_data(django_client):
    response = django_client.post('/test/123', data={"some_client_data": "123"}, content_type="application/json")
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


def test_can_block(django_client):
    r = Registry()
    r.register(SampleBlockingFilter)
    response = django_client.post('/test/123', data={"some_client_data": "123"}, content_type="application/json")
    assert response.status_code == 403
    simpleExportSpanProcessor.force_flush(1)
    span_list = memoryExporter.get_finished_spans()
    django_span = span_list[0]
    attrs = django_span.attributes
    assert attrs['http.status_code'] == 403
    r.filters.clear()
    memoryExporter.clear()

def test_wsgi_is_wrapped(django_client):
    if _INSTRUMENTATION_STATE[DJANGO_KEY]:
        del _INSTRUMENTATION_STATE[DJANGO_KEY]
    TEST_AGENT_INSTANCE._instrument(DJANGO_KEY, auto_instrument=True)
    from django.core import wsgi
    # since we cant test that its a lambda just test that our function is included in the string signature
    assert str(wsgi.get_wsgi_application).index('add_wsgi_wrapper') > 0

def test_asgi_is_wrapped(django_client):
    if _INSTRUMENTATION_STATE[DJANGO_KEY]:
        del _INSTRUMENTATION_STATE[DJANGO_KEY]
    TEST_AGENT_INSTANCE._instrument(DJANGO_KEY, auto_instrument=True)
    from django.core import asgi
    # since we cant test that its a lambda just test that our function is included in the string signature
    assert str(asgi.get_asgi_application).index('add_asgi_wrapper') > 0


