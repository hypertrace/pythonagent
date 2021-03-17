import sys
import os.path
import logging
import inspect

logger = logging.getLogger(__name__)

class BaseInstrumentorWrapper:
  def __init__(self):
    logger.debug('Entering BaseInstrumentorWrapper constructor.');
    super().__init__() 
    self._processRequestHeaders = False
    self._processResponseHeaders = False
    self._processRequestBody = False
    self._processResponseBody = False
    self._serviceName = 'hypertrace-python-agent'

  def introspect(self, obj):
    logger.debug('Describing object.')
    for func in [type, id, dir, vars, callable]:
      try:
        logger.debug("%s(%s):\t\t%s" % (func.__name__, self.introspect.__code__.co_varnames[0], func(obj)))
        logger.debug("%s: %s" % (func.__name__, inspect.getmembers(obj)))
      except Exception:
        logger.error("No data to display");

  def getProcessRequestHeaders(self):
    return self._processRequestHeaders

  def getProcessResponseHeaders(self):
    return self._processResponseHeaders

  def getProcessRequestBody(self):
    return self._processRequestBody

  def getProcessResponseBody(self):
    return self._processResponseBody

  def getServiceName(self):
    return self._serviceName

  def setProcessRequestHeaders(self, processRequestHeaders):
    logger.debug('Setting self._processRequestHeaders.')
    self._processRequestHeaders = processRequestHeaders

  def setProcessResponseHeaders(self, processResponseHeaders):
    logger.debug('Setting self._processResponseHeaders.');
    self._processResponseHeaders = processResponseHeaders

  def setProcessRequestBody(self, processRequestBody):
    logger.debug('Setting self._processRequestBody.');
    self._processRequestBody = processRequestBody

  def setProcessResponseBody(self, processResponseBody):
    logger.debug('Setting self._processResponseBody.');
    self._processResponseBody = processResponseBody

  def setServiceName(self, serviceName):
    logger.debug('Setting self._serviceName')
    self._serviceName = serviceName
