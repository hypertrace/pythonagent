'''Hypertrace flask instrumentor module wrapper.'''
import sys
import os.path
import logging
import inspect
import traceback
import json
import flask
from opentelemetry.instrumentation.flask import (
    FlaskInstrumentor,
    get_default_span_name,
    _teardown_request,
    _ENVIRON_SPAN_KEY,
)
from hypertrace.agent import constants  # pylint: disable=R0801
from hypertrace.agent.instrumentation import BaseInstrumentorWrapper

# Initialize logger
logger = logging.getLogger(__name__)  # pylint: disable=C0103

# Dump metadata about an object; useful for initial discovery of interestin ginfo


def introspect(obj) -> None:
    '''Troubleshooting assistance function for inspecting new flask-related objects'''
    logger.debug('Describing object.')
    try:
        for func in [type, id, dir, vars, callable]:
            logger.debug("%s(%s):\t\t%s",
                         func.__name__, introspect.__code__.co_varnames[0], func(obj))
        logger.debug("%s: %s", func.__name__, inspect.getmembers(obj))
    except:  # pylint: disable=W0702
        logger.error('Error dumping object: exception=%s, stacktrace=%s',
                     sys.exc_info()[0],
                     traceback.format_exc())

# Per request pre-handler
def _hypertrace_before_request(flask_wrapper):
    '''This function is invoked by flask to set the handler'''
    def hypertrace_before_request() -> None:
        '''Hypertrace before_request() method'''
        logger.debug('Entering _hypertrace_before_request().')
        try:
            # Read span from flask "environment". The global flask.request
            # object keeps track of which request belong to the currently
            # active thread. See
            #   https://flask.palletsprojects.com/en/1.1.x/api/#flask.request
            span = flask.request.environ.get(_ENVIRON_SPAN_KEY)
            # Pull request headers
            # for now, assuming single threaded mode (multiple python processes)
            request_headers = flask.request.headers
            # Pull message body
            request_body = flask.request.data       # same
            logger.debug('span: %s', str(span))
            logger.debug('Request headers: %s', str(request_headers))
            logger.debug('Request body: %s', str(request_body))
            # Call base request handler
            flask_wrapper.generic_request_handler(
                request_headers, request_body, span)
        except Exception as err:  # pylint: disable=W0703
            logger.error(constants.INST_RUNTIME_EXCEPTION_MSSG,
                         'flask before_request handler',
                         err,
                         traceback.format_exc())
            # Not rethrowing to avoid causing runtime errors for Flask.
    return hypertrace_before_request

# Per request post-handler


def _hypertrace_after_request(flask_wrapper) -> flask.wrappers.Response:
    '''This function is invoked by flask to set the handler'''
    def hypertrace_after_request(response):
        '''Hypertrace after_request method.'''
        try:
            logger.debug('Entering _hypertrace_after_request().')
            # Read span from flask "environment"
            span = flask.request.environ.get(_ENVIRON_SPAN_KEY)
            # Pull response headers
            response_headers = response.headers
            # Pull message body
            response_body = response.data
            logger.debug('Span: %s', str(span))
            logger.debug('Response Headers: %s', str(response_headers))
            logger.debug('Response Body: %s', str(response_body))
            # Call base response handler
            flask_wrapper.generic_response_handler(
                response_headers, response_body, span)
            return response
        except Exception as err:  # pylint: disable=W0703
            logger.error(constants.INST_RUNTIME_EXCEPTION_MSSG,
                         'flask after_request handler',
                         err,
                         traceback.format_exc())
            # Not rethrowing to avoid causing runtime errors for Flask.
            return response

    return hypertrace_after_request

# Main Flask Instrumentor Wrapper class.
class FlaskInstrumentorWrapper(FlaskInstrumentor, BaseInstrumentorWrapper):
    '''Hypertrace wrapper around OTel Flask instrumentor class'''

    def __init__(self):
        logger.debug('Entering FlaskInstrumentorWrapper constructor.')
        super().__init__()
        self._app = None

    # Initialize instrumentation wrapper
    def instrument_app(self, app, name_callback=get_default_span_name) -> None:
        '''Initialize instrumentation'''
        logger.debug('Entering FlaskInstrumentorWrapper.instument_app().')
        try:
            # Call parent class's initialization
            super().instrument_app(app, name_callback)
            self._app = app
            # Set pre-request handler
            app.before_request(_hypertrace_before_request(self))
            # Set post-response handler
            app.after_request(_hypertrace_after_request(self))
        except Exception as err:  # pylint: disable=W0703
            logger.error("""An error occurred initializing flask otel
                            instrumentor: exception=%s, stacktrace=%s""",
                         err,
                         traceback.format_exc())
            raise err

    # Teardown instrumentation wrapper
    def uninstrument_app(self, app) -> None:
        '''Disable instrumentation'''
        logger.debug('Entering FlaskInstrumentorWrapper.uninstrument_app()')
        try:
            # Call parent's teardown logic
            super()._uninstrument_app(self, app)  # pylint: disable=E1101
            self._app = None
        except Exception as err:  # pylint: disable=W0703
            logger.error("""An error occurred while shutting down flask otel
                         instrumentor: exception=%s, stacktrace=%s""",
                         err,
                         traceback.format_exc())
            raise err

    # retrieve flask app
    def get_app(self) -> flask.Flask:
        '''Return the flask app object.'''
        return self._app
