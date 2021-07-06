from opentelemetry.trace import Span, NonRecordingSpan

from hypertrace.agent.filter import Filter
from hypertrace.agent.filter.registry import Registry


class TestFilter(Filter):
    def evaluate_url_and_headers(self, span: Span, url: str, headers: tuple) -> bool:
        return True

    def evaluate_body(self, span: Span, body) -> bool:
        return True


def test_register():
    registry = Registry()
    registry.register(TestFilter)
    assert len(registry.filters) == 1
    registry.filters = []


def test_apply_filter_with_values_can_return_true():
    registry = Registry()
    registry.register(TestFilter)
    assert registry.apply_filters(NonRecordingSpan(None), 'a_url', ('key', 'v'), 'body_data')


def test_apply_filter_returns_false_by_default():
    registry = Registry()
    registry.register(TestFilter)
    assert registry.apply_filters(NonRecordingSpan(None), None, tuple(), None) is False
