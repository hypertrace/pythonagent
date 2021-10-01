'''Hypertrace flask instrumentor module wrapper.''' # pylint: disable=R0401
import sys
import os.path
import logging
import inspect
import traceback
import json
import flask
from opentelemetry.instrumentation.flask import (
    _InstrumentedFlask,
    FlaskInstrumentor,
    get_default_span_name,
    _teardown_request,
    _ENVIRON_SPAN_KEY,
)
from werkzeug.exceptions import Forbidden

from hypertrace.agent import constants  # pylint: disable=R0801
from hypertrace.agent.filter.registry import Registry
from hypertrace.agent.instrumentation import BaseInstrumentorWrapper
from hypertrace.agent.init import AgentInit
from hypertrace.agent.config import AgentConfig

# Initialize logger
logger = logging.getLogger(__name__)  # pylint: disable=C0103

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

            span.update_name(str(flask.request.method) + ' ' + str(flask.request.url_rule))

            # Call base request handler
            flask_wrapper.generic_request_handler(request_headers, request_body, span)

            block_result = Registry().apply_filters(span,
                                                    flask.request.url,
                                                    flask.request.headers,
                                                    flask.request.data)
            if block_result:
                logger.debug('should block evaluated to true, aborting with 403')
                flask.abort(403)

        except Forbidden as forbidden_error:
            raise forbidden_error

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

            response_body = ""
            # dont extract response content if body is a file
            if not response.direct_passthrough:
                response_body = response.data

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

class _HypertraceInstrumentedFlask(_InstrumentedFlask, BaseInstrumentorWrapper):
    """Hypertrace Wrapper class around OTel _InstrumentedFlask. This replaces
    the flask.Flask class definition."""

    def __init__(self, *args, **kwargs):
        _InstrumentedFlask.__init__(self, *args, **kwargs)
        BaseInstrumentorWrapper.__init__(self)
        self.before_request(_hypertrace_before_request(self))
        self.after_request(_hypertrace_after_request(self))
        config: AgentConfig = AgentConfig()
        self.set_process_request_headers(config.agent_config.data_capture.http_headers.request)
        self.set_process_request_body(config.agent_config.data_capture.http_body.request)
        self.set_process_response_headers(config.agent_config.data_capture.http_headers.response)
        self.set_process_response_body(config.agent_config.data_capture.http_body.response)
        self.set_body_max_size(config.agent_config.data_capture.body_max_size_bytes)

# Main Flask Instrumentor Wrapper class.
class FlaskInstrumentorWrapper(FlaskInstrumentor, BaseInstrumentorWrapper):
    '''Hypertrace wrapper around OTel Flask instrumentor class'''

    def __init__(self):
        logger.debug('Entering FlaskInstrumentorWrapper constructor.')
        super().__init__()
        self._app = None

    def with_app(self, app=None):
        """when instrumenting via code we need to instrument
        the app directly, this is conditionally called from agent.instrument"""
        self._app = app

    def instrument(self, **kwargs):
        if self._app:
            # code based instrumentation
            before_hook = _hypertrace_before_request(self)
            after_hook = _hypertrace_after_request(self)
            FlaskInstrumentorWrapper.instrument_app(self._app)
            self._app.before_request(before_hook)
            self._app.after_request(after_hook)
        else:
            # auto instrumentation
            super().instrument()


    def _instrument(self, **kwargs):
        '''Override OTel method that sets up global flask instrumentation'''
        self._original_flask = flask.Flask # pylint: disable = W0201
        name_callback = kwargs.get("name_callback")
        tracer_provider = kwargs.get("tracer_provider")
        if callable(name_callback):
            _HypertraceInstrumentedFlask.name_callback = name_callback
        _HypertraceInstrumentedFlask._tracer_provider = tracer_provider # pylint: disable=W0212
        flask.Flask = _HypertraceInstrumentedFlask

    # Initialize instrumentation wrapper
    @staticmethod
    def instrument_app(app, request_hook=None, response_hook=None, tracer_provider=None):
        '''Initialize instrumentation'''
        logger.debug('Entering FlaskInstrumentorWrapper.instument_app().')
        try:

            # Call parent class's initialization
            FlaskInstrumentor.instrument_app(app, request_hook, response_hook, None)

        except Exception as err:  # pylint: disable=W0703
            logger.error("""An error occurred initializing flask otel
                            instrumentor: exception=%s, stacktrace=%s""",
                         err,
                         traceback.format_exc())
            raise err

    # Teardown instrumentation wrapper
    @staticmethod
    def uninstrument_app(app) -> None:
        '''Disable instrumentation'''
        logger.debug('Entering FlaskInstrumentorWrapper.uninstrument_app()')
        try:
            # Call parent's teardown logic
            super().uninstrument_app(app)  # pylint: disable=E1101

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
