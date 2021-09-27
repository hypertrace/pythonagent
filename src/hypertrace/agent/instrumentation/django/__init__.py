'''Hypertrace django instrumentor module wrapper.''' # pylint: disable=R0401
import logging
import traceback

from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.trace import Span
from django.core.exceptions import PermissionDenied  # pylint:disable=C0415

from hypertrace.agent import constants
from hypertrace.agent.filter.registry import Registry
from hypertrace.agent.instrumentation import BaseInstrumentorWrapper


logger = logging.getLogger(__name__)  # pylint: disable=C0103


class DjangoInstrumentationWrapper(BaseInstrumentorWrapper):
    """wrapped class around django instrumentation"""
    def instrument(self):
        """configure django instrumentor w hooks"""
        DjangoInstrumentor().instrument(request_hook=self.request_hook,
                                        response_hook=self.response_hook)

    def request_hook(self, span: Span, request):
        """django request hook before request is processed by app"""
        try:
            body = request.body
            span.update_name(f"{request.method} {span.name}")
            self.generic_request_handler(request.headers, body, span)
            full_url = request.build_absolute_uri()
            block_result = Registry().apply_filters(span,
                                                    full_url,
                                                    request.headers,
                                                    body)
            if block_result:
                logger.debug('should block evaluated to true, aborting with 403')
                raise PermissionDenied
        except PermissionDenied as permission_denied:
            raise permission_denied
        except Exception as err:  # pylint:disable=W0703
            logger.debug(constants.INST_RUNTIME_EXCEPTION_MSSG,
                         'django request hook',
                         err,
                         traceback.format_exc())


    def response_hook(self, span, _request, response):
        """django response hook before response is written out"""
        try:
            body = response.content
            self.generic_response_handler(response.headers, body, span)
        except Exception as err:  # pylint:disable=W0703
            logger.debug(constants.INST_RUNTIME_EXCEPTION_MSSG,
                         'django response hook',
                         err,
                         traceback.format_exc())
