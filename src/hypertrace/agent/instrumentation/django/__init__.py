import logging

from hypertrace.agent.filter.registry import Registry
from hypertrace.agent.instrumentation import BaseInstrumentorWrapper

logger = logging.getLogger(__name__)  # pylint: disable=C0103

class DjangoInstrumentationWrapper(BaseInstrumentorWrapper):

    def instrument(self):
        from opentelemetry.instrumentation.django import DjangoInstrumentor
        DjangoInstrumentor().instrument(request_hook=self.request_hook, response_hook=self.response_hook)

    def request_hook(self, span, request):
        try:
            headers = list(dict(request.headers).items())
            body = request.body
            span.update_name(f"{request.method} {span.name}")
            self.generic_request_handler(headers, body, span)
            full_url = request.build_absolute_uri()
            block_result = Registry().apply_filters(span,
                                                    full_url,
                                                    headers,
                                                    body)
            if block_result:
                logger.debug('should block evaluated to true, aborting with 403')
        except:
            pass


    def response_hook(self, span, request, response):
        headers = list(dict(response.headers).items())
        body = response.content
        self.generic_response_handler(headers, body, span)
