import sys
import os.path
import logging
import inspect

class BaseInstrumentorWrapper:
  def __init__(self):
    logging.debug('Entering BaseInstrumentorWrapper constructor.');
    super().__init__() 
    self._processRequestHeaders = False
    self._processResponseHeaders = False
    self._processRequestBody = False
    self._processResponseBody = False

  def introspect(self, obj):
    logging.debug('Describing object.')
    for func in [type, id, dir, vars, callable]:
      try:
        logging.debug("%s(%s):\t\t%s" % (func.__name__, self.introspect.__code__.co_varnames[0], func(obj)))
        logging.debug("%s: %s" % (func.__name__, inspect.getmembers(obj)))
      except Exception:
        logging.error("No data to display");

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

