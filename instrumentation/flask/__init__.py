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
    logging.debug("RCBJ0100:%s: %s" % (func.__name__, inspect.getmembers(obj)))
  except Exception:
    logging.error("No data to display");

# Per request pre-handler
def _hypertrace_before_request(app):
  def hypertrace_before_request():
    logging.debug('Entering _hypertrace_before_request().');
#    logging.debug('Dumping _app.')
#    introspect(app)
    for h in flask.request.headers:
      logging.debug(str(h))
    logging.debug('Request Body: ' + str(flask.request.data))

  return hypertrace_before_request

# Per request post-handler
def _hypertrace_teardown_request(app):
  def hypertrace_teardown_request(response):
    logging.debug('Entering _hypertrace_teardown_request().')
    logging.debug('Dumping response.')
    introspect(response)
    logging.debug('Dumping app.')
#    introspect(app)
#    print(type(response.status_code))
#    print(type(response.headers))
#    introspect(str(flask.Response.get_data()))
    for h in response.headers:
      logging.debug(str(h))
    logging.debug('Response Body: ' + str(response.data))
    return response

  return hypertrace_teardown_request

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
    app.before_request(_hypertrace_before_request(self._app))
    app.after_request(_hypertrace_teardown_request(self._app))

  def _uninstrument(self, **kwargs):
    logging.debug('Entering FlaskInstrumentorWrapper._uninstrument()');
    super()._uninstrument(self, kwargs)
 
  def uninstrument_app(self, app):
    logging.debug('Entering FlaskInstrumentorWrapper.uninstrument_app()');
    super()._uninstrument_app(self, app)
    self._app = None

  def getApp():
    return self._app
