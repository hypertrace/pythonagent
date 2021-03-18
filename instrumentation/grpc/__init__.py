import sys
import os.path
import logging
import inspect
import flask
import grpc
import json
import traceback
from contextlib import contextmanager
from opentelemetry import trace
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer, GrpcInstrumentorClient, _server, _client, server_interceptor
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
    super()._instrument(**kwargs)
    self._original_wrapper_func = grpc.server

    def server_wrapper(*args, **kwargs):
      logger.debug('Entering wrapper interceptors set')
      logger.debug('Setting server_interceptor_wrapper().')
      kwargs["interceptors"] = [server_interceptor_wrapper()]
      return self._original_wrapper_func(*args, **kwargs)
    grpc.server = server_wrapper

  def _uninstrument(self, **kwargs):
    logger.debug('Entering GrpcInstrumentorServerWrapper._uninstrument()')
    super()._uninstrument(**kwargs)

class GrpcInstrumentorClientWrapper(GrpcInstrumentorServer, BaseInstrumentorWrapper):
  def __init__(self):
    logger.debug('Entering GrpcInstrumentorClientWrapper constructor.');
    super().__init__()

def server_interceptor_wrapper(tracer_provider=None):
  logger.debug('Entering server_interceptor_wrapper().')
  from . import _server
  tracer = trace.get_tracer(__name__, __version__, tracer_provider)
  logger.debug('Calling OpenTelemetryServerInterceptorWrapper(tracer).')
  return OpenTelemetryServerInterceptorWrapper(tracer)

class _OpenTelemetryWrapperServicerContext(_server._OpenTelemetryServicerContext):
    def __init__(self, servicer_context, active_span):
      super().__init__(servicer_context, active_span)

    def set_trailing_metadata(self, *args, **kwargs):
        logger.debug('RCBJ0204a: ' + str(self._active_span))
        logger.debug('RCBJ0204b: ' + str(args))
        for h in args[0]:
           logger.debug(str(h))
           self._active_span.set_attribute('rpc.response.metadata.' + h[0].lower(), h[1])
        return self._servicer_context.set_trailing_metadata(*args, **kwargs)

class OpenTelemetryServerInterceptorWrapper(_server.OpenTelemetryServerInterceptor):
  def __init__(self, tracer):
    logger.debug('Entering OpenTelemetryServerInterceptorWrapper.__init__().')
    super().__init__(tracer)

  def intercept_service(self, continuation, handler_call_details):
        logger.debug('Entering OpenTelemetryServerInterceptorWrapper.intercept_service().')
        def telemetry_wrapper(behavior, request_streaming, response_streaming):
            def telemetry_interceptor(request_or_iterator, context):
                # handle streaming responses specially
                if response_streaming:
                    return self._intercept_server_stream(
                        behavior,
                        handler_call_details,
                        request_or_iterator,
                        context,
                    )
                logger.debug('Span Object: ' + str(context._active_span))
                span = context._active_span
                #span.set_attribute('tester', 'tester')
                #dump request headers
                #introspect(handler_call_details) 
                logger.debug('RCBJ0201: ' + str(handler_call_details.invocation_metadata))
                for h in handler_call_details.invocation_metadata:
                  logger.debug(str(h))
                  span.set_attribute('rpc.request.metadata.' + h[0].lower(), h[1])
                #introspect(request_or_iterator)
                logger.debug('RCBJ0202: ' + str(request_or_iterator))
                span.set_attribute('rpc.request.body', str(request_or_iterator))
                try:
                  # Capture response
                  context = _OpenTelemetryWrapperServicerContext(context, span)
                  response = behavior(request_or_iterator, context)
                  logger.debug('RCBJ0203: ' + str(response))
                  span.set_attribute('rpc.request.body', str(response))
                  #introspect(context)
                  return response
                except Exception as error:
                  # Bare exceptions are likely to be gRPC aborts, which
                  # we handle in our context wrapper.
                  # Here, we're interested in uncaught exceptions.
                  # pylint:disable=unidiomatic-typecheck
                  if type(error) != Exception:
                    span.record_exception(error)
                    raise error
            return telemetry_interceptor
        return _server._wrap_rpc_behavior(continuation(handler_call_details), telemetry_wrapper)

  def _intercept_server_stream(self, behavior, handler_call_details, request_or_iterator, context):
    logger.debug('Entering OpenTelemetryServerInterceptorWrapper.intercept_server_stream().')
