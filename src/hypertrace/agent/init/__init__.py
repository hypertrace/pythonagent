'''Initialize all the components using configuration from AgentConfig'''
import sys
import os
import traceback
import logging
import json
from typing import Union

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, export
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.exporter.zipkin.proto.http import ZipkinExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from hypertrace.agent import constants
from hypertrace.agent.config import config_pb2, AgentConfig

# Initialize logger
logger = logging.getLogger(__name__)  # pylint: disable=C0103


class AgentInit:  # pylint: disable=R0902,R0903
    '''Initialize all the OTel components using configuration from AgentConfig'''

    def __init__(self, agent_config: AgentConfig):
        '''constructor'''
        logger.debug('Initializing AgentInit object.')
        self._config = agent_config
        self._modules_initialized = {
            "flask": False,
            "grpc:server": False,
            "grpc:client": False,
            "mysql": False,
            "postgresql": False,
            "requests": False,
            "aiohttp_client": False
        }
        self._tracer_provider = None

        try:
            self.apply_config(None)

            self._flask_instrumentor_wrapper = None
            self._grpc_instrumentor_client_wrapper = None
            self._grpc_instrumentor_server_wrapper = None
            self._mysql_instrumentor_wrapper = None
            self._postgresql_instrumentor_wrapper = None
            self._requests_instrumentor_wrapper = None
            self._aiohttp_client_instrumentor_wrapper = None

        except Exception as err:  # pylint: disable=W0703
            logger.error('Failed to initialize tracer: exception=%s, stacktrace=%s',
                         err,
                         traceback.format_exc())
            raise sys.exc_info()[0]

    def apply_config(self, agent_config: (Union[None, AgentConfig])):
        """Initialize various aspects of the agent based on the most recent config"""
        if agent_config:
            self._config = agent_config

        self.init_trace_provider()
        self.init_propagation()

        if self._config.use_console_span_exporter():
            self.set_console_span_processor()
        else:
            self.init_exporter()


    def init_trace_provider(self) -> None:
        '''Initialize trace provider and set resource attributes.'''
        resource_attributes = {
            "service.name": self._config.agent_config.service_name,
            "service.instance.id": os.getpid(),
            "telemetry.sdk.version": constants.TELEMETRY_SDK_VERSION,
            "telemetry.sdk.name": constants.TELEMETRY_SDK_NAME,
            "telemetry.sdk.language": constants.TELEMETRY_SDK_LANGUAGE
        }
        if self._config.agent_config.resource_attributes:
            logger.debug(
                'Custom attributes found. Adding to resource attributes dict.')
            resource_attributes.update(
                self._config.agent_config.resource_attributes)
        self._tracer_provider = TracerProvider(
            resource=Resource.create(resource_attributes)
        )
        trace.set_tracer_provider(self._tracer_provider)

    def init_exporter(self) -> None:
        """Initialize exporter"""
        reporter_type = self._config.agent_config.reporting.trace_reporter_type
        if reporter_type == config_pb2.TraceReporterType.ZIPKIN:
            self._init_zipkin_exporter()
        elif reporter_type == config_pb2.TraceReporterType.OTLP:
            self._init_otlp_exporter()
        else:
            logger.error("Unknown exporter type `%s`", reporter_type)

    def init_propagation(self) -> None:
        '''Initialize requested context propagation protocols.'''
        propagator_list = []
        for prop_format in self._config.agent_config.propagation_formats:
            if prop_format == config_pb2.PropagationFormat.TRACECONTEXT:
                from opentelemetry.trace.propagation.tracecontext \
                  import TraceContextTextMapPropagator # pylint: disable=C0415
                propagator_list += [ TraceContextTextMapPropagator() ]
                logger.debug('Adding TRACECONTEXT trace propagator to list.')
            if prop_format == config_pb2.PropagationFormat.B3:
                from opentelemetry.propagators.b3 import B3Format  # pylint: disable=C0415
                propagator_list += [ B3Format() ]
                logger.debug('Adding B3 trace propagator to list.')

        if len(propagator_list) == 0:
            logger.debug('No propagators have been initialized.')

        logger.debug('propagator_list: %s', str(propagator_list))
        from opentelemetry.propagate import set_global_textmap # pylint: disable=C0415
        from opentelemetry.propagators.composite import CompositePropagator # pylint: disable=C0415
        composite_propagators = CompositePropagator(propagator_list)
        set_global_textmap(composite_propagators)

    def dump_config(self) -> None:
        '''dump the current state of AgentInit.'''
        logger.debug('Calling DumpConfig().')
        for mod in self._modules_initialized:
            logger.debug('%s : %s', mod, str(self._modules_initialized[mod]))

    # Creates a flask wrapper using the config defined in hypertraceconfig
    def init_instrumentation_flask(self, app) -> None:
        '''Creates a flask instrumentation wrapper using the config defined in hypertraceconfig'''
        logger.debug('Calling AgentInit.flaskInit().')
        try:
            if self.is_registered('flask'):
                return
            from hypertrace.agent.instrumentation.flask import FlaskInstrumentorWrapper  # pylint: disable=C0415
            self._modules_initialized['flask'] = True
            self._flask_instrumentor_wrapper = FlaskInstrumentorWrapper()
            call_default_instrumentor = True
            # There are two ways to initialize the flask instrumenation
            # wrapper. The first (and original way) instruments the specific
            # Flask object that is passed in). The second way is to globally
            # replace the Flask class definition with the hypertrace instrumentation
            # wrapper class.
            #
            # If an app object is provided, then the flask wrapper is initialized
            # by calling the instrument_app method. Then, there is no need to call
            # instrument() (so, we pass False as the second argument to
            # self.init_instrumentor_wrapper_base_for_http().
            #
            # If no app object was provided, then instrument() is called.

            from hypertrace.agent.instrumentation.flask import _hypertrace_before_request # pylint: disable=C0415
            from hypertrace.agent.instrumentation.flask import _hypertrace_after_request # pylint: disable=C0415
            before_hook = _hypertrace_before_request(self._flask_instrumentor_wrapper)
            after_hook = _hypertrace_after_request(self._flask_instrumentor_wrapper)
            if app:
                FlaskInstrumentorWrapper.instrument_app(app)
                call_default_instrumentor = False

                app.before_request(before_hook)
                # Set post-response handler
                app.after_request(after_hook)
            self.init_instrumentor_wrapper_base_for_http(self._flask_instrumentor_wrapper,
                                                         call_default_instrumentor)
        except Exception as err:  # pylint: disable=W0703
            logger.error(constants.INST_WRAP_EXCEPTION_MSSG,
                         'flask',
                         err,
                         traceback.format_exc())

    def init_instrumentation_grpc_server(self) -> None:
        '''Creates a grpc server wrapper based on hypertrace config'''
        logger.debug('Calling AgentInit.grpcServerInit')
        try:
            if self.is_registered('grpc:server'):
                return
            from hypertrace.agent.instrumentation.grpc import (  # pylint: disable=C0415
                GrpcInstrumentorServerWrapper
            )
            self._modules_initialized['grpc:server'] = True
            self._grpc_instrumentor_server_wrapper = GrpcInstrumentorServerWrapper()
            self._grpc_instrumentor_server_wrapper.instrument()

            self._grpc_instrumentor_server_wrapper.set_process_request_headers(
                self._config.agent_config.data_capture.http_headers.request)
            self._grpc_instrumentor_server_wrapper.set_process_request_body(
                self._config.agent_config.data_capture.http_body.request)

            self._grpc_instrumentor_server_wrapper.set_process_response_headers(
                self._config.agent_config.data_capture.http_headers.response)
            self._grpc_instrumentor_server_wrapper.set_process_response_body(
                self._config.agent_config.data_capture.http_body.response)
        except Exception as err:  # pylint: disable=W0703
            logger.error(constants.INST_WRAP_EXCEPTION_MSSG,
                         'grpc:server',
                         err,
                         traceback.format_exc())

    # Creates a grpc client wrapper using the config defined in hypertraceconfig
    def init_instrumentation_grpc_client(self) -> None:
        '''Creates a grpc client wrapper using the config defined in hypertraceconfig'''
        logger.debug('Calling AgentInit.grpcClientInit')
        try:
            if self.is_registered('grpc:client'):
                return
            from hypertrace.agent.instrumentation.grpc import (  # pylint: disable=C0415
                GrpcInstrumentorClientWrapper
            )
            self._modules_initialized['grpc:client'] = True

            self._grpc_instrumentor_client_wrapper = GrpcInstrumentorClientWrapper()
            self._grpc_instrumentor_client_wrapper.instrument()

            self._grpc_instrumentor_client_wrapper.set_process_request_headers(
                self._config.agent_config.data_capture.http_headers.request)
            self._grpc_instrumentor_client_wrapper.set_process_request_body(
                self._config.agent_config.data_capture.http_body.request)

            self._grpc_instrumentor_client_wrapper.set_process_response_headers(
                self._config.agent_config.data_capture.http_headers.response)
            self._grpc_instrumentor_client_wrapper.set_process_response_body(
                self._config.agent_config.data_capture.http_body.response)
        except Exception as err:  # pylint: disable=W0703
            logger.error(constants.INST_WRAP_EXCEPTION_MSSG,
                         'grpc:client',
                         err,
                         traceback.format_exc())

    # Creates a mysql server wrapper using the config defined in hypertraceconfig
    def init_instrumentation_mysql(self) -> None:
        '''Creates a mysql server wrapper using the config defined in hypertraceconfig'''
        logger.debug('Calling AgentInit.mysqlInit()')
        try:
            if self.is_registered('mysql'):
                return
            from hypertrace.agent.instrumentation.mysql import (  # pylint: disable=C0415
                MySQLInstrumentorWrapper
            )
            self._modules_initialized['mysql'] = True
            self._mysql_instrumentor_wrapper = MySQLInstrumentorWrapper()
            self.init_instrumentor_wrapper_base_for_http(
                self._mysql_instrumentor_wrapper)
        except Exception as err:  # pylint: disable=W0703
            logger.error(constants.INST_WRAP_EXCEPTION_MSSG,
                         'mysql',
                         err,
                         traceback.format_exc())

    # Creates a postgresql client wrapper using the config defined in hypertraceconfig
    def init_instrumentation_postgresql(self) -> None:
        '''Creates a postgresql client wrapper using the config defined in hypertraceconfig'''
        logger.debug('Calling AgentInit.postgreSQLInit()')
        try:
            if self.is_registered('postgresql'):
                return
            from hypertrace.agent.instrumentation.postgresql import (  # pylint: disable=C0415
                PostgreSQLInstrumentorWrapper
            )
            self._modules_initialized['postgresql'] = True
            self._postgresql_instrumentor_wrapper = PostgreSQLInstrumentorWrapper()
            self.init_instrumentor_wrapper_base_for_http(
                self._postgresql_instrumentor_wrapper)
        except Exception as err:  # pylint: disable=W0703
            logger.error(constants.INST_WRAP_EXCEPTION_MSSG,
                         'postgresql',
                         err,
                         traceback.format_exc())

    # Creates a requests client wrapper using the config defined in hypertraceconfig
    def init_instrumentation_requests(self) -> None:
        '''Creates a requests client wrapper using the config defined in hypertraceconfig'''
        logger.debug('Calling AgentInit.requestsInit()')
        try:
            if self.is_registered('requests'):
                return
            from hypertrace.agent.instrumentation.requests import (  # pylint: disable=C0415
                RequestsInstrumentorWrapper
            )
            self._modules_initialized['requests'] = True
            self._requests_instrumentor_wrapper = RequestsInstrumentorWrapper()
            self.init_instrumentor_wrapper_base_for_http(
                self._requests_instrumentor_wrapper)
        except Exception as err:  # pylint: disable=W0703
            logger.error(constants.INST_WRAP_EXCEPTION_MSSG,
                         'requests',
                         err,
                         traceback.format_exc())

    # Creates an aiohttp-client wrapper using the config defined in hypertraceconfig
    def aiohttp_client_init(self) -> None:
        '''Creates an aiohttp-client wrapper using the config defined in hypertraceconfig'''
        logger.debug('Calling AgentInit.aioHttpClientInit()')
        try:
            if self.is_registered('aiohttp_client'):
                return
            from hypertrace.agent.instrumentation.aiohttp import (  # pylint: disable=C0415
                AioHttpClientInstrumentorWrapper
            )
            self._modules_initialized['aiohttp_client'] = True
            self._aiohttp_client_instrumentor_wrapper = AioHttpClientInstrumentorWrapper()
            self.init_instrumentor_wrapper_base_for_http(
                self._aiohttp_client_instrumentor_wrapper)
        except Exception as err:  # pylint: disable=W0703
            logger.error(constants.INST_WRAP_EXCEPTION_MSSG,
                         'aiohttp_client',
                         err,
                         traceback.format_exc())

    # Common wrapper initialization logic
    def init_instrumentor_wrapper_base_for_http(self,
                                                instrumentor,
                                                call_instrument: bool = True) -> None:
        '''Common wrapper initialization logic'''
        logger.debug('Calling AgentInit.initInstrumentorWrapperBaseForHTTP().')
        if call_instrument:
            instrumentor.instrument()
        instrumentor.set_process_request_headers(
            self._config.agent_config.data_capture.http_headers.request)
        instrumentor.set_process_request_body(
            self._config.agent_config.data_capture.http_body.request)
        instrumentor.set_process_response_headers(
            self._config.agent_config.data_capture.http_headers.response)
        instrumentor.set_process_response_body(
            self._config.agent_config.data_capture.http_body.response)
        instrumentor.set_body_max_size(
            self._config.agent_config.data_capture.body_max_size_bytes)

    def register_processor(self, processor) -> None:
        '''Register additional span exporter + processor'''
        logger.debug('Entering AgentInit.register_processor().')
        self._tracer_provider.add_span_processor(processor)

    def set_console_span_processor(self) -> None:
        '''Register the console span processor for debugging purposes.'''
        logger.debug('Entering AgentInit.setConsoleSpanProcessor().')
        console_span_exporter = ConsoleSpanExporter(
            service_name=self._config.agent_config.service_name)
        simple_export_span_processor = SimpleSpanProcessor(
            console_span_exporter)
        self._tracer_provider.add_span_processor(simple_export_span_processor)

    def _init_zipkin_exporter(self) -> None:
        '''Initialize Zipkin exporter'''
        try:
            zipkin_exporter = ZipkinExporter(
                endpoint=self._config.agent_config.reporting.endpoint
            )

            span_processor = BatchSpanProcessor(zipkin_exporter)
            self._tracer_provider.add_span_processor(span_processor)

            logger.info(
                'Initialized Zipkin exporter reporting to `%s`',
                self._config.agent_config.reporting.endpoint)
        except Exception as err:  # pylint: disable=W0703
            logger.error('Failed to initialize Zipkin exporter: exception=%s, stacktrace=%s',
                         err,
                         traceback.format_exc())

    def _init_otlp_exporter(self) -> None:
        '''Initialize OTLP exporter'''
        try:
            otlp_exporter = OTLPSpanExporter(endpoint=self._config.agent_config.reporting.endpoint,
                                             insecure= \
                                               not self._config.agent_config.reporting.secure)
            span_processor = BatchSpanProcessor(otlp_exporter)
            self._tracer_provider.add_span_processor(span_processor)

            logger.info('Initialized OTLP exporter reporting to `%s`',
                        self._config.agent_config.reporting.endpoint)
        except Exception as err:  # pylint: disable=W0703
            logger.error('Failed to initialize OTLP exporter: exception=%s, stacktrace=%s',
                         err,
                         traceback.format_exc())

    def is_registered(self, module: str) -> bool:
        '''Is an instrumentation module already registered?'''
        try:
            return self._modules_initialized[module]
        except Exception as err: # pylint: disable=W0703,W0612
            return False
