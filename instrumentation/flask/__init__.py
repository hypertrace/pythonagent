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
  _ENVIRON_SPAN_KEY,
)

# Initialize logger
logger = logging.getLogger(__name__)

# Dump metadata about an object; useful for initial discovery of interestin ginfo
def introspect(obj):
  logger.debug('Describing object.')
  try:
    for func in [type, id, dir, vars, callable]:
      logger.debug("%s(%s):\t\t%s" % (func.__name__, introspect.__code__.co_varnames[0], func(obj)))
    logger.debug("%s: %s" % (func.__name__, inspect.getmembers(obj)))
  except:
    logger.error('Error dumping object: exception=%s, stacktrace=%s',
      sys.exc_info()[0],
      traceback.format_exc())

# Per request pre-handler
def _hypertrace_before_request( flaskWrapper, app):
  # This function is actually invoked by flask
  def hypertrace_before_request():
    logger.debug('Entering _hypertrace_before_request().');
    try:
      # Read span from flask "environment". The global flask.request
      # object keeps track of which request belong to the currently
      # active thread. See 
      #   https://flask.palletsprojects.com/en/1.1.x/api/#flask.request
      span = flask.request.environ.get(_ENVIRON_SPAN_KEY)
      # Pull request headers
      requestHeaders = flask.request.headers # for now, assuming single threaded mode (multiple python processes)
      # Pull message body
      requestBody = flask.request.data       # same
      logger.debug('span: ' + str(span))
      logger.debug('Request Headers: ' + str(requestBody))
      logger.debug('Request Body: ' + str(requestBody))
      # Call base request handler
      flaskWrapper.genericRequestHandler(requestHeaders, requestBody, span)
    except:
      logger.error('An error occurred in flask before_request handler: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      #Not rethrowing to avoid causing runtime errors for Flask.
  return hypertrace_before_request

# Per request post-handler
def _hypertrace_after_request(flaskWrapper, app):
  def hypertrace_after_request(response):
    try:
      logger.debug('Entering _hypertrace_after_request().')
      # Read span from flask "environment"
      span = flask.request.environ.get(_ENVIRON_SPAN_KEY)
      # Pull response headers
      responseHeaders = response.headers
      # Pull message body
      responseBody = response.data
      logger.debug('Span: ' + str(span))
      logger.debug('Response Headers: ' + str(responseHeaders))
      logger.debug('Response Body: ' + str(responseBody))
      # Call base response handler
      flaskWrapper.genericResponseHandler(responseHeaders, responseBody, span)
      return response
    except:
      logger.error('An error occurred in flask after_request handler: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      #Not rethrowing to avoid causisng runtime errors for Flask
  return hypertrace_after_request

# Main Flask Instrumentor Wrapper class.
class FlaskInstrumentorWrapper(FlaskInstrumentor, BaseInstrumentorWrapper):
  def __init__(self):
    logger.debug('Entering FlaskInstrumentorWrapper constructor.');
    super().__init__() 

  # Initialize instrumentation wrapper
  def instrument_app(self, app, name_callback=get_default_span_name):
    logger.debug('Entering FlaskInstrumentorWrapper.instument_app().')
    try:
      # Call parent class's initialization
      super().instrument_app(app, name_callback)
      self._app = app
      # Set pre-request handler
      app.before_request(_hypertrace_before_request(self, self._app))
      # Set post-response handler
      app.after_request(_hypertrace_after_request(self, self._app))
    except:
      logger.error('An error occurred initializing flask otel instrumentor: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise e

  # Teardown instrumentation wrapper
  def uninstrument_app(self, app):
    logger.debug('Entering FlaskInstrumentorWrapper.uninstrument_app()');
    try:
      # Call parent's teardown logic
      super()._uninstrument_app(self, app)
      self._app = None
    except:
      logger.error('An error occurred while shutting down flask otel instrumentor: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise e

  # retrieve flask app
  def getApp():
    return self._app
