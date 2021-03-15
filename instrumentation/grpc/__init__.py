import sys
import os.path
import logging
import inspect
import flask
import grpc
import traceback
from contextlib import contextmanager
from opentelemetry import trace
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer, GrpcInstrumentorClient, _server, _client
from opentelemetry.instrumentation.grpc.version import __version__
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
    traceback.print_exc()

class GrpcInstrumentorServerWrapper(GrpcInstrumentorServer, BaseInstrumentorWrapper):
  def __init__(self):
    logger.debug('Entering GrpcInstrumentorServerWrapper constructor.');
    super().__init__() 

  def instrument(self):
    logger.debug('Entering GrpcInstrumentorServerWrapper.instument().')
    super().instrument()

  def uninstrument(self):
    logger.debug('Entering GrpcInstrumentorServerWrapper.uninstrument()')
    super().uninstrument()

  def _instrument(self, **kwargs):
    logger.debug('Entering GrpcInstrumentorServerWrapper._instument().')
#    super()._instrument(**kwargs)
    self._original_wrapper_func = grpc.server

    def server(*args, **kwargs):
      logger.debug('Entering wrapper interceptors set')
      if "interceptors" in kwargs:
        # add our interceptor as the first
        logger.debug('Setting server_interceptor_wrapper() as interceptor')
        kwargs["interceptors"].insert(1, server_interceptor_wrapper())
      else:
        kwargs["interceptors"] = [server_interceptor_wrapper()]
      return self._original_wrapper_func(*args, **kwargs)

    grpc.server = server
    
  def _uninstrument(self, **kwargs):
    logger.debug('Entering GrpcInstrumentorServerWrapper._uninstrument()')
    super()._uninstrument(**kwargs)

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

def client_interceptor_wrapper(tracer_provider=None):
  from . import _client
  tracer = trace.get_tracer(__name__, __version__, tracer_provider)
  return OpenTelemetryClientInterceptor(tracer)

def server_interceptor_wrapper(tracer_provider=None):
  from . import _server
  tracer = trace.get_tracer(__name__, __version__, tracer_provider)
  return OpenTelemetryServerInterceptorWrapper(tracer)

class OpenTelemetryServerInterceptorWrapper(_server.OpenTelemetryServerInterceptor):
  def __init__(self, tracer):
    logger.debug('Entering OpenTelemetryServerInterceptorWrapper.__init__().')
    super().__init__(tracer)

#  @contextmanager
  def _set_remote_context(self, servicer_context):
    logger.debug('Entering OpenTelemetryServerInterceptorWrapper._set_remote_context().')
    super()._set_remote_context(servicer_context)

  def _start_span(self, handler_call_details, context):
    logger.debug('Entering OpenTelemetryServerInterceptorWrapper._start_span().')
    super()._start_span(handler_call_details, context)

  def intercept_service(self, continuation, handler_call_details):
    logger.debug('Entering OpenTelemetryServerInterceptorWrapper.intercept_service().')
    super().intercept_service(continuation, handler_call_details)

  def _intercept_server_stream(self, behavior, handler_call_details, request_or_iterator, context):
    logger.debug('Entering OpenTelemetryServerInterceptorWrapper.intercept_server_stream().')
    super()._intercept_server_stream(behavior, handler_call_details, request_or_iterator, context)

class OpenTelemetryClientInterceptorWrapper(_client.OpenTelemetryClientInterceptor):
  def __init(self, tracer):
    super().__init__(tracer)
