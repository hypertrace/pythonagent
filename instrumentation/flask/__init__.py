import sys
import os.path
import logging
import inspect
import flask
import traceback
import json
from instrumentation import BaseInstrumentorWrapper
from opentelemetry.instrumentation.flask import (
  FlaskInstrumentor,
  get_default_span_name,
  _teardown_request,
  _ENVIRON_STARTTIME_KEY,
  _ENVIRON_SPAN_KEY,
  _ENVIRON_ACTIVATION_KEY,
  _ENVIRON_TOKEN
)

logger = logging.getLogger(__name__)

def introspect(obj):
  logger.debug('Describing object.')
  try:
    for func in [type, id, dir, vars, callable]:
      logger.debug("%s(%s):\t\t%s" % (func.__name__, introspect.__code__.co_varnames[0], func(obj)))
    logger.debug("%s: %s" % (func.__name__, inspect.getmembers(obj)))
  except:
    e = sys.exc_info()[0]
    logger.error("No data to display")
    traceback.print_exc()
    raise e

# Per request pre-handler
def _hypertrace_before_request( flaskWrapper, app):
  def hypertrace_before_request():
    logger.debug('Entering _hypertrace_before_request().');
    try:
      span = flask.request.environ.get(_ENVIRON_SPAN_KEY)
      requestHeaders = flask.request.headers # for now, assuming single threaded mode (multiple python processes)
      requestBody = flask.request.data       # same
      logger.debug('span: ' + str(span))
      logger.debug('Request Headers: ' + str(requestBody))
      logger.debug('Request Body: ' + str(requestBody))
      flaskWrapper.genericRequestHandler(requestHeaders, requestBody, span)
    except:
      logger.error('An error occurred in flask before_request handler: exception=%s, stacktrace=%s', sys.exc_info()[0], traceback.format_exc())
      #Not rethrowing to avoid causing runtime errors for Flask.
  return hypertrace_before_request

# Per request post-handler
def _hypertrace_after_request(flaskWrapper, app):
  def hypertrace_after_request(response):
    try:
      logger.debug('Entering _hypertrace_after_request().')
      span = flask.request.environ.get(_ENVIRON_SPAN_KEY)
      logger.debug('Span: ' + str(span))
      logger.debug('Response Headers: ' + str(response.headers))
      logger.debug('Response Body: ' + str(response.data))
      flaskWrapper.genericResponseHandler(response.headers, response.data, span)
      return response
    except:
      logger.error('An error occurred in flask after_request handler: exception=%s, stacktrace=%s', sys.exc_info()[0], traceback.format_exc())
      #Not rethrowing to avoid cuaisng runtime errors for Flask
  return hypertrace_after_request

# Main Flask Instrumentor Wrapper class.
class FlaskInstrumentorWrapper(FlaskInstrumentor, BaseInstrumentorWrapper):
  def __init__(self):
    logger.debug('Entering FlaskInstrumentorWrapper constructor.');
    super().__init__() 

  def instrument_app(self, app, name_callback=get_default_span_name):
    logger.debug('Entering FlaskInstrumentorWrapper.instument_app().')
    try:
      super().introspect(app)
      super().instrument_app(app, name_callback)
      super().introspect(app)
      self._app = app
      app.before_request(_hypertrace_before_request(self, self._app))
      app.after_request(_hypertrace_after_request(self, self._app))
    except:
      logger.error('An error occurred initializing flask otel instrumentor: exception=%s, stacktrace=%s', sys.exc_info()[0], traceback.format_exc())
      raise e

  def uninstrument_app(self, app):
    logger.debug('Entering FlaskInstrumentorWrapper.uninstrument_app()');
    try:
      super()._uninstrument_app(self, app)
      self._app = None
    except:
      logger.error('An error occurred while shutting down flask otel instrumentor: exception=%s, stacktrace=%s', sys.exc_info()[0], traceback.format_exc())
      raise e

  def getApp():
    return self._app
