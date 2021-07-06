'''Hypertrace wrapper around OTel Flask instrumentor'''
import sys
import os.path
import logging
import inspect
import json
import traceback
from contextlib import contextmanager
import flask
import grpc
from opentelemetry import propagators, trace
from opentelemetry.instrumentation.grpc import (
    GrpcInstrumentorServer,
    GrpcInstrumentorClient,
    _server,
    _client,
    server_interceptor
)
from opentelemetry.instrumentation.grpc.version import __version__
from opentelemetry.instrumentation.grpc.grpcext import intercept_channel
from wrapt import wrap_function_wrapper as _wrap # pylint: disable=R0801
from hypertrace.agent import constants
from hypertrace.agent.filter.registry import Registry
from hypertrace.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger with local module name
logger = logging.getLogger(__name__) # pylint: disable=C0103

# Object introspection, used for debugging purposes
def introspect(obj) -> None:
    '''Object introspection, used for debugging purposes'''
    logger.debug('Describing object.')
    try:
        for func in [type, id, dir, vars, callable]:
            logger.debug("%s(%s):\t\t%s",
                         func.__name__, introspect.__code__.co_varnames[0], func(obj))
        logger.debug("%s: %s", func.__name__, inspect.getmembers(obj))
    except Exception as err: # pylint: disable=W0703
        logger.error('No data to display, exception=%s, stacktrace=%s',
                     err,
                     traceback.print_exc())

# The main entry point for a wrapper around the OTel grpc:server instrumentation module
class GrpcInstrumentorServerWrapper(GrpcInstrumentorServer, BaseInstrumentorWrapper):
    '''Hypertrace wrapper around OTel grpc:server instrumentor class'''
    # Construtor
    def __init__(self):
        '''constructor'''
        logger.debug('Entering GrpcInstrumentorServerWrapper constructor.')
        super().__init__()
        self._original_wrapper_func = None

    # Enable wrapper instrumentation
    def instrument(self, **kwargs) -> None:
        '''instrument grpc:server'''
        logger.debug('Entering GrpcInstrumentorServerWrapper.instument().')
        super().instrument()

    # Remove wrapper instrumentation
    def uninstrument(self, **kwargs) -> None:
        '''disable grpc:server instrumentation.'''
        logger.debug('Entering GrpcInstrumentorServerWrapper.uninstrument()')
        super().uninstrument()

    # Internal enable wrapper instrumentation
    def _instrument(self, **kwargs) -> None:
        '''Enable wrapper instrumentation internal call'''
        logger.debug('Entering GrpcInstrumentorServerWrapper._instument().')
        super()._instrument(**kwargs)
        self._original_wrapper_func = grpc.server

        def server_wrapper(*args, **kwargs) -> None:
            logger.debug('Entering wrapper interceptors set')
            logger.debug(
                'Setting server_interceptor_wrapper() as interceptor.')
            kwargs["interceptors"] = [server_interceptor_wrapper(self)]
            return self._original_wrapper_func(*args, **kwargs)
        grpc.server = server_wrapper

    # Internal disable wrapper instrumentation
    def _uninstrument(self, **kwargs) -> None:
        '''Disable wrapper instrumentation internal call'''
        logger.debug('Entering GrpcInstrumentorServerWrapper._uninstrument()')
        super()._uninstrument(**kwargs)

# The main entry point for a wrapper around the OTel grpc:client instrumentation module
class GrpcInstrumentorClientWrapper(GrpcInstrumentorClient, BaseInstrumentorWrapper):
    '''Hypertrace wrapper around OTel grpc:client instrumentor class'''
    # constructor
    def __init__(self):
        '''constructor'''
        logger.debug('Entering GrpcInstrumentorClientWrapper constructor.')
        super().__init__()

    # Internal initialize instrumentation
    def _instrument(self, **kwargs) -> None:
        '''Internal initialize instrumentation'''
        logger.debug('Entering GrpcInstrumentorClientWrapper._instrument().')
        super()._instrument(**kwargs)
# Uncomment this to reenable the client handler.
#    for ctype in self._which_channel(kwargs):
#      _wrap(
#        "grpc", ctype, self.wrapper_fn_wrapper,
#    )

    # Internal disable instrumentation
    def _uninstrument(self, **kwargs) -> None:
        '''Internal disable instrumentation'''
        logger.debug('Entering GrpcInstrumentorClientWrapper._uninstrument().')
        super()._uninstrument(**kwargs)

    # Wrap function for initializing the the request handler
    def wrapper_fn_wrapper(self, original_func, instance, args, kwargs) -> None: # pylint: disable=W0613,R0201
        '''Wrap function for initializing the the request handler'''
        channel = original_func(*args, **kwargs)
        tracer_provider = kwargs.get("tracer_provider")
        return intercept_channel(
            channel, client_interceptor_wrapper(
                tracer_provider=tracer_provider),
        )

# Initialize the server handler
def server_interceptor_wrapper(gisw, tracer_provider=None) -> None:
    '''Helper function to set interceptor.'''
    logger.debug('Entering server_interceptor_wrapper().')
    tracer = trace.get_tracer(__name__, __version__, tracer_provider)
    return OpenTelemetryServerInterceptorWrapper(tracer, gisw)

# Initialize the client handler
def client_interceptor_wrapper(tracer_provider) -> None:
    '''Helper function to set interceptor.'''
    logger.debug('Entering client_interceptor_wrapper().')
    tracer = trace.get_tracer(__name__, __version__, tracer_provider)
    return OpenTelemetryClientInterceptorWrapper(tracer)

# Wrapper around Server-side telemetry context
class _OpenTelemetryWrapperServicerContext(_server._OpenTelemetryServicerContext): # pylint: disable=W0212,W0223
    '''grpc:server telemetry context'''
    def __init__(self, servicer_context, active_span):
        '''constructor'''
        logger.debug(
            'Entering _OpenTelemetryWrapperServicerContext.__init__().')
        super().__init__(servicer_context, active_span)
        self._response_headers = ()

    def set_trailing_metadata(self, *args, **kwargs) -> None:
        """Override trailing metadata(response headers) method.
        Allows us to capture the response headers"""
        logger.debug(
            'Entering _OpenTelemetryWrapperServicerContext.set_trailing_metadata().')
        logger.debug('Span Object: %s', str(self._active_span))
        logger.debug('Response Headers: %s', str(args))
        self._response_headers = args
        return self._servicer_context.set_trailing_metadata(*args, **kwargs)

    def get_trailing_metadata(self) -> tuple:
        '''Return response headers'''
        return self._response_headers

# Wrapper around server-side interceptor


class OpenTelemetryServerInterceptorWrapper(_server.OpenTelemetryServerInterceptor): # pylint: disable=R0903
    '''Hypertrace wrapper around OTel grpc:server Instrumentor class'''
    def __init__(self, tracer, gisw):
        '''constructor'''
        logger.debug(
            'Entering OpenTelemetryServerInterceptorWrapper.__init__().')
        super().__init__(tracer)
        self._gisw = gisw

    def intercept_service(self, continuation, handler_call_details):
        '''Setup interceptor'''
        logger.debug(
            'Entering OpenTelemetryServerInterceptorWrapper.intercept_service().')

        def telemetry_wrapper(behavior, request_streaming, response_streaming): # pylint: disable=W0613
            '''Setup interceptor helper for unary requests.'''
            logger.debug(
                'Entering OpenTelemetryServerInterceptorWrapper.telemetry_wrapper().')

            def telemetry_interceptor(request_or_iterator, context) -> None:
                '''Process request for hypertrace.'''
                logger.debug(
                    'Entering OpenTelemetryServerInterceptorWrapper.telemetry_interceptor().')
                # handle streaming responses specially
                if response_streaming:
                    return self._intercept_server_stream(
                        behavior,
                        handler_call_details,
                        request_or_iterator,
                        context,
                    )
                logger.debug('Span Object: %s', str(context._active_span)) # pylint: disable=W0212
                span = context._active_span # pylint: disable=W0212
                logger.debug('Request Metadata: %s',
                             str(handler_call_details.invocation_metadata))
                logger.debug('Request Body: %s', str(request_or_iterator))

                invocation_metadata = handler_call_details.invocation_metadata

                self._gisw.generic_rpc_request_handler(
                    invocation_metadata, request_or_iterator, span)
                try:
                    block_result = Registry().apply_filters(span,
                                                            '',
                                                            invocation_metadata,
                                                            request_or_iterator)
                    if block_result:
                        logger.debug('should block evaluated to true, aborting with 403')
                        return context.abort(grpc.StatusCode.PERMISSION_DENIED, 'Permission Denied')

                    # Capture response
                    context = _OpenTelemetryWrapperServicerContext(
                        context, span)
                    response = behavior(request_or_iterator, context)
                    logger.debug('Response Body: %s', str(response))
                    logger.debug('Response Headers: %s',
                                 str(context.get_trailing_metadata()))
                    trailing_metadata = context.get_trailing_metadata()
                    if len(trailing_metadata) > 0:
                        self._gisw.generic_rpc_response_handler(
                            trailing_metadata[0], response, span)

                    return response
                except Exception as error: # pylint: disable=W0703
                    # Bare exceptions are likely to be gRPC aborts, which
                    # we handle in our context wrapper.
                    # Here, we're interested in uncaught exceptions.
                    # pylint:disable=unidiomatic-typecheck
                    if type(error) != Exception:
                        span.record_exception(error)
                        raise error
                    return None
            return telemetry_interceptor
        return _server._wrap_rpc_behavior(continuation(handler_call_details), telemetry_wrapper) # pylint: disable=W0212

    def _intercept_server_stream(
            self,
            behavior,
            handler_call_details,
            request_or_iterator,
            context) -> None:
        '''Setup interceptor helper for streaming requests.'''
        logger.debug(
            'Entering OpenTelemetryServerInterceptorWrapper.intercept_server_stream().')
        # COME_BACK -- need to implement this

# Wrapper around client-side interceptor
class OpenTelemetryClientInterceptorWrapper(_client.OpenTelemetryClientInterceptor):
    '''Hypertrace wrapper around OTel grpc:client instrumentor class.'''
    def __init__(self, tracer):
        '''constructor'''
        logger.debug(
            'Entering OpenTelemetryClientInterceptorWrapper.__init__().')
        super().__init__(tracer)

    def intercept_unary(self, request, metadata, client_info, invoker) -> None:
        '''Process unary request for hypertrace.'''
        logger.debug(
            'Entering OpenTelemetryClientInterceptorWrapper.intercept_unary().')
        try:
            # Not sure how to obtain span object here
            logger.debug('request: %s', str(request))
            logger.debug('metadata: %s', str(metadata))
            result = invoker(request, metadata)
            logger.debug('result: %s', str(result))
            # Not sure how to obtain trailing metadata here
        except grpc.RpcError as err:
            logger.error(constants.INST_RUNTIME_EXCEPTION_MSSG,
                         'processing client request',
                         err,
                         traceback.format_exc())
            raise err

#        return self._trace_result(result)

    def intercept_stream(
            self,
            request_or_iterator,
            metadata,
            client_info,
            invoker
    ) -> None:
        '''process streaming request for hypertrace'''
        logger.debug(
            'Entering OpenTelemetryClientInterceptorWrapper.intercept_stream().')
        # COME_BACK -- need to implement this
