import sys
import os.path
import logging
import inspect
import flask;
from opentelemetry.instrumentation.flask import FlaskInstrumentor, get_default_span_name, _teardown_request, _ENVIRON_STARTTIME_KEY, _ENVIRON_SPAN_KEY, _ENVIRON_ACTIVATION_KEY, _ENVIRON_TOKEN
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from instrumentation import BaseInstrumentorWrapper

logger = logging.getLogger(__name__)

def introspect(obj):
  logger.debug('Describing object.')
  try:
    for func in [type, id, dir, vars, callable]:
      logger.debug("%s(%s):\t\t%s" % (func.__name__, introspect.__code__.co_varnames[0], func(obj)))
    logger.debug("%s: %s" % (func.__name__, inspect.getmembers(obj)))
  except Exception:
    logger.error("No data to display");

# Per request pre-handler
def _hypertrace_before_request( flaskWrapper, app):
  def hypertrace_before_request():
    logger.debug('Entering _hypertrace_before_request().');
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
        span.set_attribute('http.request.header.' + h[0], h[1])
    if flaskWrapper.getProcessRequestBody():
      logger.debug('Request Body: ' + str(flask.request.data))
      span.set_attribute('http.request.body', str(flask.request.data))
  return hypertrace_before_request

# Per request post-handler
def _hypertrace_after_request(flaskWrapper, app):
  def hypertrace_after_request(response):
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
        span.set_attribute('http.response.header.' + h[0], h[1])
    if flaskWrapper.getProcessResponseBody():
      logger.debug('Response Body: ' + str(response.data))
      span.set_attribute('http.response.body', str(response.data))
    return response
  return hypertrace_after_request

class FlaskInstrumentorWrapper(FlaskInstrumentor, BaseInstrumentorWrapper):
  def __init__(self):
    logger.debug('Entering FlaskInstrumentorWrapper constructor.');
    super().__init__() 

  def instrument_app(self, app, name_callback=get_default_span_name):
    logger.debug('Entering FlaskInstrumentorWrapper.instument_app().')
    super().introspect(app)
    super().instrument_app(app, name_callback)
    super().introspect(app)
    self._app = app
    app.before_request(_hypertrace_before_request(self, self._app))
    app.after_request(_hypertrace_after_request(self, self._app))

  def uninstrument_app(self, app):
    logger.debug('Entering FlaskInstrumentorWrapper.uninstrument_app()');
    super()._uninstrument_app(self, app)
    self._app = None

  def getApp():
    return self._app
