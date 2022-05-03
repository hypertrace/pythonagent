import os

import pytest
from opentelemetry.trace import Span

from hypertrace.agent import Agent, _uninstrument_all
from hypertrace.agent.filter import Filter
from hypertrace.agent.filter.registry import Registry
from hypertrace.agent.instrumentation import instrumentation_definitions
from tests import configure_inmemory_span_exporter


class SampleBlockingFilter(Filter):

    def evaluate_url_and_headers(self, span: Span, url: str, headers: tuple, request_type) -> bool:
        return True

    def evaluate_body(self, span: Span, body, headers: dict, request_type) -> bool:
        pass


class SampleBodyBlockingFilter(Filter):
    def evaluate_url_and_headers(self, span: Span, url: str, headers: tuple, request_type) -> bool:
        return False

    def evaluate_body(self, span: Span, body, headers: dict, request_type) -> bool:
        return True


@pytest.fixture
def agent():
    # we never want to export spans to default exporter
    os.environ['HT_ENABLE_CONSOLE_SPAN_EXPORTER'] = 'true'

    # new patches will just replace old ones which allows us to call `agent.instrument()` during each test
    _uninstrument_all()
    Agent._instance = None
    agent = Agent()

    return agent

@pytest.fixture
def agent_with_filter(agent):
    Registry().register(SampleBlockingFilter)
    yield agent
    Registry().filters = []

@pytest.fixture
def agent_with_body_filter(agent):
    Registry().register(SampleBodyBlockingFilter)
    yield agent
    Registry().filters = []



@pytest.fixture
def exporter(agent):
    exporter = configure_inmemory_span_exporter(agent)

    yield exporter

    exporter.clear()