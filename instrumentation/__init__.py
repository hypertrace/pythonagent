import sys
import os.path
import logging

class BaseInstrumentorWrapper:
  def __init__(self):
    logging.debug('Entering BaseInstrumentorWrapper constructor.');
    super().__init__() 

  def introspect(self, obj):
    logging.debug('Describing object.')
    for func in [type, id, dir, vars, callable]:
      try:
        logging.debug("%s(%s):\t\t%s" % (func.__name__, introspect.__code__.co_varnames[0], func(obj)))
        logging.debug("%s: %s" % func.__name__, inspect.getmembers(obj))
      except Exception:
        logging.error("No data to display");
