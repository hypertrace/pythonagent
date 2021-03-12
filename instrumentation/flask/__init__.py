import sys
import os.path
import logging
import inspect
import flask;
from opentelemetry.instrumentation.flask import FlaskInstrumentor, get_default_span_name, _teardown_request, _ENVIRON_STARTTIME_KEY, _ENVIRON_SPAN_KEY, _ENVIRON_ACTIVATION_KEY, _ENVIRON_TOKEN
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from instrumentation import BaseInstrumentorWrapper

def introspect(obj):
  logging.debug('Describing object.')
  try:
    for func in [type, id, dir, vars, callable]:
      logging.debug("%s(%s):\t\t%s" % (func.__name__, introspect.__code__.co_varnames[0], func(obj)))
    logging.debug("%s: %s" % (func.__name__, inspect.getmembers(obj)))
  except Exception:
    logging.error("No data to display");

# Per request pre-handler
def _hypertrace_before_request( flaskWrapper, app):
  def hypertrace_before_request():
    logging.debug('Entering _hypertrace_before_request().');
    activation = flask.request.environ.get(_ENVIRON_ACTIVATION_KEY)
    span = flask.request.environ.get(_ENVIRON_SPAN_KEY)
    token = flask.request.environ.get(_ENVIRON_TOKEN)
    logging.debug('activation: ' + str(activation))
    logging.debug('token: ' + str(token))
    logging.debug('span: ' + str(span))
    if span.is_recording():
      logging.debug('Span is Recording!')
    if flaskWrapper.getProcessRequestHeaders():
      logging.debug('Dumping Request Headers:')
      for h in flask.request.headers:
        logging.debug(str(h))
        span.set_attribute('http.request.header.' + h[0], h[1])
    if flaskWrapper.getProcessRequestBody():
      logging.debug('Request Body: ' + str(flask.request.data))
      span.set_attribute('http.request.body', str(flask.request.data))
  return hypertrace_before_request

# Per request post-handler
def _hypertrace_after_request(flaskWrapper, app):
  def hypertrace_after_request(response):
    logging.debug('Entering _hypertrace_after_request().')
    logging.debug('Dumping response.')
    introspect(response)
    activation = flask.request.environ.get(_ENVIRON_ACTIVATION_KEY)
    span = flask.request.environ.get(_ENVIRON_SPAN_KEY)
    token = flask.request.environ.get(_ENVIRON_TOKEN)
    logging.debug('activation: ' + str(activation))
    logging.debug('token: ' + str(token))
    logging.debug('span: ' + str(span))
    if flaskWrapper.getProcessResponseHeaders():
      logging.debug('Dumping Response Headers.')
      for h in response.headers:
        logging.debug(str(h))
        span.set_attribute('http.response.header.' + h[0], h[1])
    if flaskWrapper.getProcessResponseBody():
      logging.debug('Response Body: ' + str(response.data))
      span.set_attribute('http.response.body', str(response.data))
    return response
  return hypertrace_after_request

class FlaskInstrumentorWrapper(FlaskInstrumentor, BaseInstrumentorWrapper):
  def __init__(self):
    logging.debug('Entering FlaskInstrumentorWrapper constructor.');
    super().__init__() 

  def instrument_app(self, app, name_callback=get_default_span_name):
    logging.debug('Entering FlaskInstrumentorWrapper.instument_app().')
    super().introspect(app)
    super().instrument_app(app, name_callback)
    super().introspect(app)
    self._app = app
    app.before_request(_hypertrace_before_request(self, self._app))
    app.after_request(_hypertrace_after_request(self, self._app))

#  def _uninstrument(self, **kwargs):
#    logging.debug('Entering FlaskInstrumentorWrapper._uninstrument()');
#    super()._uninstrument(self, kwargs)
 
  def uninstrument_app(self, app):
    logging.debug('Entering FlaskInstrumentorWrapper.uninstrument_app()');
    super()._uninstrument_app(self, app)
    self._app = None

  def getApp():
    return self._app
