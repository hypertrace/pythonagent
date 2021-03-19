import sys
import os.path
import logging
import inspect
import flask
import grpc
import json
import traceback
from contextlib import contextmanager
from opentelemetry import propagators, trace
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer, GrpcInstrumentorClient, _server, _client, server_interceptor
from opentelemetry.instrumentation.grpc.version import __version__
from instrumentation import BaseInstrumentorWrapper
from opentelemetry.instrumentation.grpc.grpcext import intercept_channel
from wrapt import wrap_function_wrapper as _wrap

#Initialize logger with local module name
logger = logging.getLogger(__name__)

#Object introspection, used for debugging purposes
def introspect(obj):
  logger.debug('Describing object.')
  try:
    for func in [type, id, dir, vars, callable]:
      logger.debug("%s(%s):\t\t%s" % (func.__name__, introspect.__code__.co_varnames[0], func(obj)))
    logger.debug("%s: %s" % (func.__name__, inspect.getmembers(obj)))
  except Exception:
    logger.error("No data to display");
    traceback.print_exc()

# The main entry point for a wrapper around the OTel grpc instrumentation module
class GrpcInstrumentorServerWrapper(GrpcInstrumentorServer, BaseInstrumentorWrapper):
  # Construtor
  def __init__(self):
    logger.debug('Entering GrpcInstrumentorServerWrapper constructor.');
    super().__init__() 

  # Enable wrapper instrumentation
  def instrument(self):
    logger.debug('Entering GrpcInstrumentorServerWrapper.instument().')
    super().instrument()

  # Remove wrapper instrumentation
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

class GrpcInstrumentorClientWrapper(GrpcInstrumentorClient, BaseInstrumentorWrapper):
  def __init__(self):
    logger.debug('Entering GrpcInstrumentorClientWrapper constructor.');
    super().__init__()

  def _instrument(self, **kwargs):
    logger.debug('Entering GrpcInstrumentorClientWrapper._instrument().')
    super()._instrument(**kwargs)
    for ctype in self._which_channel(kwargs):
      _wrap(
        "grpc", ctype, self.wrapper_fn_wrapper,
    )

  def _uninstrument(self, **kwargs):
    logger.debug('Entering GrpcInstrumentorClientWrapper._uninstrument().')
    super()._uninstrument(**kwargs)
    for ctype in self._which_channel(kwargs):
      unwrap(grpc, ctype)

  def wrapper_fn_wrapper(self, original_func, instance, args, kwargs):
    channel = original_func(*args, **kwargs)
    tracer_provider = kwargs.get("tracer_provider")
    return intercept_channel(
      channel, client_interceptor_wrapper(tracer_provider=tracer_provider),
    )

def server_interceptor_wrapper(tracer_provider=None):
  logger.debug('Entering server_interceptor_wrapper().')
  tracer = trace.get_tracer(__name__, __version__, tracer_provider)
  logger.debug('Calling OpenTelemetryServerInterceptorWrapper(tracer).')
  return OpenTelemetryServerInterceptorWrapper(tracer)

def client_interceptor_wrapper(tracer_provider):
  logger.debug('Entering client_interceptor_wrapper().')
  tracer = trace.get_tracer(__name__, __version__, tracer_provider)
  return OpenTelemetryClientInterceptorWrapper(tracer)

class _OpenTelemetryWrapperServicerContext(_server._OpenTelemetryServicerContext):
  def __init__(self, servicer_context, active_span):
    logger.debug('Entering _OpenTelemetryWrapperServicerContext.__init__().')
    super().__init__(servicer_context, active_span)

  def set_trailing_metadata(self, *args, **kwargs):
    logger.debug('Entering _OpenTelemetryWrapperServicerContext.set_trailing_metadata().')
    logger.debug('Span Object: ' + str(self._active_span))
    logger.debug('Response Headers: ' + str(args))
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
        logger.debug('Entering OpenTelemetryServerInterceptorWrapper.telemetry_wrapper().')
            def telemetry_interceptor(request_or_iterator, context):
                logger.debug('Entering OpenTelemetryServerInterceptorWrapper.telemetry_interceptor().')
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
                logger.debug('Request Metadata: ' + str(handler_call_details.invocation_metadata))
                for h in handler_call_details.invocation_metadata:
                  logger.debug(str(h))
                  span.set_attribute('rpc.request.metadata.' + h[0].lower(), h[1])
                #introspect(request_or_iterator)
                logger.debug('Request Body: ' + str(request_or_iterator))
                span.set_attribute('rpc.request.body', str(request_or_iterator))
                try:
                  # Capture response
                  context = _OpenTelemetryWrapperServicerContext(context, span)
                  response = behavior(request_or_iterator, context)
                  logger.debug('Response Body: ' + str(response))
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
    # COME_BACK -- need to implement this

class OpenTelemetryClientInterceptorWrapper(_client.OpenTelemetryClientInterceptor):
    def __init__(self, tracer):
      logger.debug('Entering OpenTelemetryClientInterceptorWrapper.__init__().')
      super().__init__(tracer)
   
    def intercept_unary(self, request, metadata, client_info, invoker):
      logger.debug('Entering OpenTelemetryClientInterceptorWrapper.intercept_unary().')
      try:
        # Not sure how to obtain span object here
        logger.debug('RCBJ0400: ' + str(request))
        logger.debug('RCBJ0401: ' + str(metadata))
        result = invoker(request, metadata)
        logger.debug('RCBJ402: ' + str(result))
        # Not sure how to obtain trailing metadata here
      except grpc.RpcError as err:
        logger.error('An error occurred processing client_request: exception=%s, stacktrace=%s', sys.exc_info()[0], traceback.format_exc())
        raise err
      return self._trace_result(guarded_span, rpc_info, result)

    def intercept_stream(
        self, request_or_iterator, metadata, client_info, invoker
    ):
      logger.debug('Entering OpenTelemetryClientInterceptorWrapper.intercept_stream().')
      # COME_BACK -- need to implement this
