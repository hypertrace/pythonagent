"""Used for holding filters to apply to ingress traffic"""

from typing import Union, Type
from opentelemetry.trace import Span

from hypertrace.agent.filter import Filter

TYPE_HTTP = 'http'
TYPE_RPC = 'rpc'

class Registry:
    """
    Registry is used to register and apply request filters
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Registry, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.filters = []

    def register(self, filter_class: Type[Filter]):
        '''Register a filter to apply on ingress traffic'''
        instance = filter_class()
        self.filters.append(instance)

    def apply_filters(self, span: Span, url: Union[str, None], headers: dict, body, request_type) -> bool: # pylint:disable=R0913,R0917
        '''Apply all registered filters'''
        if url or headers:
            for filter_instance in self.filters:
                if filter_instance.evaluate_url_and_headers(span, url, headers, request_type):
                    return True

        if body:
            for filter_instance in self.filters:
                if filter_instance.evaluate_body(span, body, headers, request_type):
                    return True

        return False
