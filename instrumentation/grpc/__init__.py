import sys
import os.path
import logging
import inspect
import flask;
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer, GrpcInstrumentorClient
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

class GrpcInstrumentorServerWrapper(GrpcInstrumentorServer, BaseInstrumentorWrapper):
  def __init__(self):
    logger.debug('Entering GrpcInstrumentorServerWrapper constructor.');
    super().__init__() 

  def instrument(self):
    logger.debug('Entering GrpcInstrumentorServerWrapper.instument().')
    super().instrument()

  def uninstrument(self):
    logger.debug('Entering GrpcInstrumentorServerWrapper.uninstrument()');
    super().uninstrument()

class GrpcInstrumentorClientWrapper(GrpcInstrumentorClient, BaseInstrumentorWrapper):
  def __init__(self):
    logger.debug('Entering GrpcInstrumentorClientWrapper constructor.')
    super().__init__()

  def instrument(self):
    logger.debug('Entering GrpcInstrumentorClientWrapper.instrument().')
    super().instrument()

  def uninstrument(self):
    logger.debug('Entering GrpcInstrumentorClientWrapper.uninstrument().')
    super()._uninstrument()
