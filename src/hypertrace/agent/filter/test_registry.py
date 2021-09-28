'''Unittest for filter registration'''
from opentelemetry.trace import Span, NonRecordingSpan

from hypertrace.agent.filter import Filter
from hypertrace.agent.filter.registry import Registry

class TestFilter(Filter):
    '''Example of a filter that always returns true'''
    def evaluate_url_and_headers(self, span: Span, url: str, headers: dict) -> bool:
        return True

    def evaluate_body(self, span: Span, body) -> bool:
        return True

def test_register():
    '''Assert that a filter can added to the registry filter list'''
    registry = Registry()
    registry.register(TestFilter)
    assert len(registry.filters) == 1
    registry.filters = []

def test_apply_filter_with_values_can_return_true():
    '''Assert that apply_filters will return true when a filter returns true'''
    registry = Registry()
    registry.register(TestFilter)
    assert registry.apply_filters(NonRecordingSpan(None), 'a_url', {'key': 'v'}, 'body_data')

def test_apply_filter_returns_false_by_default():
    '''Assert that apply_filters will return false by default'''
    registry = Registry()
    registry.register(TestFilter)
    assert registry.apply_filters(NonRecordingSpan(None), None, {}, None) is False
