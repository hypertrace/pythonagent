import sys
import os.path
import logging
import inspect
import flask;
from opentelemetry.instrumentation.flask import FlaskInstrumentor, get_default_span_name, _teardown_request
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
    logging.info('RCBJ0001' + str(flaskWrapper.getProcessRequestHeaders()))
    if flaskWrapper.getProcessRequestHeaders():
      logging.debug('Dumping Request Headers:')
      for h in flask.request.headers:
        logging.debug(str(h))
    if flaskWrapper.getProcessRequestBody():
      logging.debug('Request Body: ' + str(flask.request.data))
  return hypertrace_before_request

# Per request post-handler
def _hypertrace_after_request(flaskWrapper, app):
  def hypertrace_after_request(response):
    logging.debug('Entering _hypertrace_after_request().')
    logging.debug('Dumping response.')
    introspect(response)
    logging.debug('Dumping app.')
    if flaskWrapper.getProcessResponseHeaders():
      logging.debug('Dumping Response Headers.')
      for h in response.headers:
        logging.debug(str(h))
    if flaskWrapper.getProcessResponseBody():
      logging.debug('Response Body(RCBJ0002): ' + str(response.data))
    return response
  return hypertrace_after_request

class FlaskInstrumentorWrapper(FlaskInstrumentor, BaseInstrumentorWrapper):
  def __init__(self):
    logging.debug('Entering FlaskInstrumentorWrapper constructor.');
    super().__init__() 
    self._processRequestHeaders = False
    self._processResponseHeaders = False
    self._processRequestBody = False
    self._processResponseBody = False

  def instrument_app(self, app, name_callback=get_default_span_name):
    logging.debug('Entering FlaskInstrumentorWrapper.instument_app().')
    super().introspect(app)
    super().instrument_app(app, name_callback)
    super().introspect(app)
    self._app = app
    app.before_request(_hypertrace_before_request(self, self._app))
    app.after_request(_hypertrace_after_request(self, self._app))

  def _uninstrument(self, **kwargs):
    logging.debug('Entering FlaskInstrumentorWrapper._uninstrument()');
    super()._uninstrument(self, kwargs)
 
  def uninstrument_app(self, app):
    logging.debug('Entering FlaskInstrumentorWrapper.uninstrument_app()');
    super()._uninstrument_app(self, app)
    self._app = None

  def getApp():
    return self._app

  def getProcessRequestHeaders(self):
    return self._processRequestHeaders

  def getProcessResponseHeaders(self):
    return self._processResponseHeaders

  def getProcessRequestBody(self):
    return self._processRequestBody

  def getProcessResponseBody(self):
    return self._processResponseBody

  def setProcessRequestHeaders(self, processRequestHeaders):
    logging.debug('Setting self._processRequestHeaders.')
    self._processRequestHeaders = processRequestHeaders

  def setProcessResponseHeaders(self, processResponseHeaders):
    logging.debug('Setting self._processResponseHeaders.');
    self._processResponseHeaders = processResponseHeaders

  def setProcessRequestBody(self, processRequestBody):
    logging.debug('Setting self._processRequestBody.');
    self._processRequestBody = processRequestBody

  def setProcessResponseBody(self, processResponseBody):
    logging.debug('Setting self._processResponseBody.');
    self._processResponseBody = processResponseBody
