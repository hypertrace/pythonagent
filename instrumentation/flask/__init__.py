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
      activation = flask.request.environ.get(_ENVIRON_ACTIVATION_KEY)
      span = flask.request.environ.get(_ENVIRON_SPAN_KEY)
      token = flask.request.environ.get(_ENVIRON_TOKEN)
      logger.debug('activation: ' + str(activation))
      logger.debug('token: ' + str(token))
      logger.debug('span: ' + str(span))
      if span.is_recording():
        logger.debug('Span is Recording!')
      if flaskWrapper.getProcessRequestHeaders():
        logger.debug('Dumping Request Headers:')
        for h in flask.request.headers:
          logger.debug(str(h))
          span.set_attribute('http.request.header.' + h[0].lower(), h[1])
      if flaskWrapper.getProcessRequestBody():
        logger.debug('Request Body: ' + str(flask.request.data))
        contentTypeHeaderTuple = [item for item in flask.request.headers if item[0].lower() == 'content-type']
        logger.debug('contentTypeHeaderTuple=' + str(contentTypeHeaderTuple))
        if len(contentTypeHeaderTuple) > 0:
          logger.debug('Found content-type header.')        
          if contentTypeHeaderTuple[0][1] != None and contentTypeHeaderTuple[0][1] != '':
            logger.debug('Mimetype/content-type value exists. %s', contentTypeHeaderTuple[0][1])
            if isInterestingContentType(contentTypeHeaderTuple[0][1]):
              logger.debug('This is an interesting content-type.')
              if contentTypeHeaderTuple[0][1] == 'application/json':
                span.set_attribute('http.request.body', json.dumps(json.loads(flask.request.data.decode('UTF8').replace("'", '"'))))
              else:
                span.set_attribute('http.request.body', str(flask.request.data.decode('UTF8')))
    except:
      logger.error('An error occurred in flask before_request handler: exception=%s, stacktrace=%s', sys.exc_info()[0], traceback.format_exc())
      #Not rethrowing to avoid causing runtime errors for Flask.
  return hypertrace_before_request

# Per request post-handler
def _hypertrace_after_request(flaskWrapper, app):
  def hypertrace_after_request(response):
    try:
      logger.debug('Entering _hypertrace_after_request().')
      logger.debug('Dumping response.')
      introspect(response)
      activation = flask.request.environ.get(_ENVIRON_ACTIVATION_KEY)
      span = flask.request.environ.get(_ENVIRON_SPAN_KEY)
      token = flask.request.environ.get(_ENVIRON_TOKEN)
      logger.debug('activation: ' + str(activation))
      logger.debug('token: ' + str(token))
      logger.debug('span: ' + str(span))
      if flaskWrapper.getProcessResponseHeaders():
        logger.debug('Dumping Response Headers.')
        for h in response.headers:
          logger.debug(str(h))
          span.set_attribute('http.response.header.' + h[0].lower(), h[1])
      if flaskWrapper.getProcessResponseBody():
        logger.debug('Response Body: ' + str(response.data))
        contentTypeHeaderTuple = [item for item in response.headers if item[0].lower() == 'content-type']
        logger.debug('contentTypeHeaderTuple=' + str(contentTypeHeaderTuple))
        if len(contentTypeHeaderTuple) > 0:
          logger.debug('Found content-type header.')
          if contentTypeHeaderTuple[0][1] != None and contentTypeHeaderTuple[0][1] != '':
            logger.debug('Mimetype/content-type value exists. %s', contentTypeHeaderTuple[0][1])
            if isInterestingContentType(contentTypeHeaderTuple[0][1]):
              logger.debug('This is an interesting content-type.')
              if contentTypeHeaderTuple[0][1] == 'application/json':
                span.set_attribute('http.request.body', json.dumps(json.loads(response.data.decode('UTF8').replace("'", '"'))))
              else:
                span.set_attribute('http.request.body', str(response.data.decode('UTF8')))
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

def isInterestingContentType(contentType):
  logger.debug('Entering FlaskInstrumentorWrapper.isInterestingContentType().')
  try:
    if contentType == 'application/json': return True
    if contentType == 'application/graphql': return True
    if contentType == 'application/x-www-form-urlencoded': return True
    return False;
  except:
    logger.error('An error occurred while inspecting content-type: exception=%s, stacktrace=%s', sys.exc_info()[0], traceback.format_exc())
    return False
