import sys
import os.path
import logging
import traceback
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import functools
import types
from requests.models import Response
from hypertrace.agent.instrumentation import BaseInstrumentorWrapper

#Initialize logger with local module name
logger = logging.getLogger(__name__)

def get_active_span_for_call_wrapper(requestsWrapper):
  logger.debug('Entering get_active_span_for_call_wrapper().')
  def get_active_span_for_call(span, response):
    logger.debug('Entering get_active_span_for_request().')
    logger.debug('span: ' + str(span))
    logger.debug('response: ' + str(response))
    logger.debug('response headers: ' + str(response.headers))
    responseContent = None
    if hasattr(response, 'content'):
      logger.debug('Converting response message body to string.')
      responseContent = response.content.decode()
    else:
      logger.debug('No response message body. Setting to blank string.')
      responseContent = ''
    logger.debug('response body: ' + str(responseContent))
    logger.debug('request: ' + str(response.request))
    logger.debug('request headers: ' + str(response.request.headers))
    requestContent = None
    if hasattr(response.request, 'content'):
      logger.debug('Converting request message body to string.')
      requestContent = response.request.content.decode()
    else:
      logger.debug('No request message body. Setting to blank string.')
      requestContent = ''
    logger.debug('request body: ' + str(requestContent))
    if span.is_recording():
      logger.debug('Span is recording.')
      requestHeaders = [(k, v) for k, v in response.request.headers.items()]
      responseHeaders = [(k, v) for k, v in response.headers.items()]
      requestsWrapper.genericRequestHandler(requestHeaders, requestContent, span)
      requestsWrapper.genericResponseHandler(responseHeaders, responseContent, span)
  return get_active_span_for_call

class RequestsInstrumentorWrapper(RequestsInstrumentor, BaseInstrumentorWrapper):
  # Constructor
  def __init__(self):
    logger.debug('Entering RequestsInstrumentorWrapper.__init__().')
    super().__init__()

  def _instrument(self, **kwargs):
    super()._instrument(
      tracer_provider=kwargs.get("tracer_provider"),
      span_callback=get_active_span_for_call_wrapper(self),
      name_callback=kwargs.get("name_callback"),
    )

  def _uninstrument(self, **kwargs):
    super()._uninstrument()
    _uninstrument()
