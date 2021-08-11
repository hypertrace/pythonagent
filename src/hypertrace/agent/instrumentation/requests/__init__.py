'''Hypertrace wrapper around OTel instrumentation class'''
import sys
import os.path
import logging
import traceback
import functools
import types
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from requests.models import Response
from hypertrace.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__) # pylint: disable=C0103

def get_active_span_for_call_wrapper(requests_wrapper):
    '''Helper function to setup call wrapper function'''
    logger.debug('Entering get_active_span_for_call_wrapper().')

    def get_active_span_for_call(span, response) -> None:
        '''Hypertrace call wrapper function'''
        logger.debug('Entering get_active_span_for_request().')
        logger.debug('span: %s', str(span))
        logger.debug('response: %s', str(response))
        logger.debug('response headers: %s', str(response.headers))
        response_content = None
        if hasattr(response, 'content'):
            logger.debug('Converting response message body to string.')
            response_content = response.content.decode()
        else:
            logger.debug('No response message body. Setting to blank string.')
            response_content = ''
        logger.debug('response body: %s', str(response_content))
        logger.debug('request: %s', str(response.request))
        logger.debug('request headers: %s', str(response.request.headers))
        request_content = None
        if hasattr(response.request, 'content'):
            logger.debug('Converting request message body to string.')
            request_content = response.request.content.decode()
        else:
            logger.debug('No request message body. Setting to blank string.')
            request_content = ''
        logger.debug('request body: %s', str(request_content))
        if span.is_recording():
            logger.debug('Span is recording.')
            request_headers = [(k, v)
                               for k, v in response.request.headers.items()] # pylint: disable=R1721
            response_headers = [(k, v) for k, v in response.headers.items()] #pylint: disable=R1721
            requests_wrapper.generic_request_handler(
                request_headers, request_content, span)
            requests_wrapper.generic_response_handler(
                response_headers, response_content, span)
    return get_active_span_for_call

def hypertrace_name_callback(method, url) -> str:
    '''generate span name'''
    logger.debug('Entering hypertrace_name_callback(), method=%s, url=%s.', method, url)
    return method + ' ' + url

class RequestsInstrumentorWrapper(RequestsInstrumentor, BaseInstrumentorWrapper):
    '''Hypertrace wrapper around OTel requests instrumentor class'''
    # Constructor
    def __init__(self):
        logger.debug('Entering RequestsInstrumentorWrapper.__init__().')
        super().__init__()

    def _instrument(self, **kwargs) -> None:
        '''internal enable instrumentation'''
        super()._instrument(
            tracer_provider=kwargs.get("tracer_provider"),
            span_callback=get_active_span_for_call_wrapper(self),
            name_callback=hypertrace_name_callback
        )

    def _uninstrument(self, **kwargs) -> None:
        '''internal disable instrumentation'''
        super()._uninstrument()
