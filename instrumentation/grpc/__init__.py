import sys
import os.path
import logging
import inspect
import flask;
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer, GrpcInstrumentorClient
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

class GrpcInstrumentorServerWrapper(GrpcInstrumentorServer, BaseInstrumentorWrapper):
  def __init__(self):
    logging.debug('Entering GrpcInstrumentorServerWrapper constructor.');
    super().__init__() 

  def instrument(self):
    logging.debug('Entering GrpcInstrumentorServerWrapper.instument().')
    super().instrument()

  def uninstrument(self):
    logging.debug('Entering GrpcInstrumentorServerWrapper.uninstrument()');
    super().uninstrument()

class GrpcInstrumentorClientWrapper(GrpcInstrumentorClient, BaseInstrumentorWrapper):
  def __init__(self):
    logging.debug('Entering GrpcInstrumentorClientWrapper constructor.')
    super().__init__()

  def instrument(self):
    logging.debug('Entering GrpcInstrumentorClientWrapper.instrument().')
    super().instrument()

  def uninstrument(self):
    logging.debug('Entering GrpcInstrumentorClientWrapper.uninstrument().')
    super()._uninstrument()
