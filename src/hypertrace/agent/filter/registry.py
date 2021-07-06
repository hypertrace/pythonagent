from typing import Union

from opentelemetry.trace import Span


class Registry:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Registry, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.filters = []

    def register(self, filter_class):
        print('registered filter')
        instance = filter_class()
        self.filters.append(instance)

    def apply_filters(self, span: Span, url: Union[str, None], headers: tuple, body) -> bool:
        if url or headers:
            for filter_instance in self.filters:
                if filter_instance.evaluate_url_and_headers(span, url, headers):
                    return True

        if body:
            for filter_instance in self.filters:
                if filter_instance.evaluate_body(span, body):
                    return True

        return False
