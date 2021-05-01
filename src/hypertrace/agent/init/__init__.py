'''Initialize all the components using configuration from AgentConfig'''
import sys
import os
import traceback
import logging
import json
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

        try:
            self._tracer_provider = None
            self.init_trace_provider()

            if self._config.use_console_span_exporter():
                self.set_console_span_processor()

            if not self._config.use_console_span_exporter():
                self.set_zipkin_processor()
                self.set_otlp_processor()

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
            logger.debug('Custom attributes found. Adding to resource attributes dict.')
            resource_attributes.update(self._config.agent_config.resource_attributes)
        self._tracer_provider = TracerProvider(
            resource=Resource.create(resource_attributes)
        )
        trace.set_tracer_provider(self._tracer_provider)

    def init_propagation(self) -> None:
        '''Initialize requested context propagation protocols.'''
        for prop_format in self._config.agent_config.propagation_formats:
            if prop_format == config_pb2.PropagationFormat.B3:
                from opentelemetry.propagate import set_global_textmap  # pylint: disable=C0415
                from opentelemetry.propagators.b3 import B3Format  # pylint: disable=C0415
                set_global_textmap(B3Format())

    def dump_config(self) -> None:
        '''dump the current state of AgentInit.'''
        logger.debug('Calling DumpConfig().')
        for mod in self._modules_initialized:
            logger.debug('%s : %s', mod, str(self._modules_initialized[mod]))

    # Creates a flask wrapper using the config defined in hypertraceconfig
    def flask_init(self, app) -> None:
        '''Creates a flask instrumentation wrapper using the config defined in hypertraceconfig'''
        logger.debug('Calling AgentInit.flaskInit().')
        try:
            from hypertrace.agent.instrumentation.flask import FlaskInstrumentorWrapper  # pylint: disable=C0415
            self._modules_initialized['flask'] = True
            self._flask_instrumentor_wrapper = FlaskInstrumentorWrapper()
            self._flask_instrumentor_wrapper.instrument_app(app)
            self.init_instrumentor_wrapper_base_for_http(
                self._flask_instrumentor_wrapper)
            self.init_propagation()
        except Exception as err:  # pylint: disable=W0703
            logger.error(constants.INST_WRAP_EXCEPTION_MSSG,
                         'flask',
                         err,
                         traceback.format_exc())

    def init_instrumentation_grpc_server(self) -> None:
        '''Creates a grpc server wrapper based on hypertrace config'''
        logger.debug('Calling AgentInit.grpcServerInit')
        try:
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
            from hypertrace.agent.instrumentation.requests import (  # pylint: disable=C0415
                RequestsInstrumentorWrapper
            )
            self._modules_initialized['requests'] = True
            self._requests_instrumentor_wrapper = RequestsInstrumentorWrapper()
            self.init_instrumentor_wrapper_base_for_http(
                self._requests_instrumentor_wrapper)
            self.init_propagation()
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
            from hypertrace.agent.instrumentation.aiohttp import (  # pylint: disable=C0415
                AioHttpClientInstrumentorWrapper
            )
            self._modules_initialized['aiohttp_client'] = True
            self._aiohttp_client_instrumentor_wrapper = AioHttpClientInstrumentorWrapper()
            self.init_instrumentor_wrapper_base_for_http(
                self._aiohttp_client_instrumentor_wrapper)
            self.init_propagation()
        except Exception as err:  # pylint: disable=W0703
            logger.error(constants.INST_WRAP_EXCEPTION_MSSG,
                         'aiohttp_client',
                         err,
                         traceback.format_exc())

    # Common wrapper initialization logic
    def init_instrumentor_wrapper_base_for_http(self, instrumentor) -> None:
        '''Common wrapper initialization logic'''
        logger.debug('Calling AgentInit.initInstrumentorWrapperBaseForHTTP().')
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

    def set_zipkin_processor(self) -> None:
        '''configure zipkin span exporter + processor'''
        if 'HT_TRACES_EXPORTER' in os.environ:
            if os.environ['HT_TRACES_EXPORTER'] == 'zipkin':
                logger.debug(
                    "HT_TRACES_EXPORTER is zipkin, adding exporter.")
            else:
                return
        else:
            if self._config.agent_config.reporting.trace_reporter_type == 'ZIPKIN':
                logger.debug("Trace reporter type is zipkin, adding exporter.")
            else:
                return

        try:
            zipkin_exporter = ZipkinExporter(
                endpoint=self._config.agent_config.reporting.endpoint
            )

            span_processor = BatchSpanProcessor(zipkin_exporter)
            self._tracer_provider.add_span_processor(span_processor)

            logger.info('Added ZipkinExporter span exporter')
        except Exception as err:  # pylint: disable=W0703
            logger.error('Failed to register_processor: exception=%s, stacktrace=%s',
                         err,
                         traceback.format_exc())

    def set_otlp_processor(self) -> None:
        '''configure otlp span exporter + processor'''
        if 'HT_TRACES_EXPORTER' in os.environ:
            if os.environ['HT_TRACES_EXPORTER'] == 'otlp':
                logger.debug("HT_TRACES_EXPORTER is otlp, adding exporter.")
            else:
                return
        else:
            if self._config.agent_config.reporting.trace_reporter_type == 'OTLP':
                logger.debug("Trace reporter type is otlp, adding exporter.")
            else:
                return

        try:
            otlp_exporter = OTLPSpanExporter(endpoint=self._config.agent_config.reporting.endpoint,
                                             insecure=self._config.agent_config.reporting.secure)
            span_processor = BatchSpanProcessor(otlp_exporter)
            self._tracer_provider.add_span_processor(span_processor)

            logger.info('Added OtlpExporter span exporter')
        except Exception as err:  # pylint: disable=W0703
            logger.error('Failed to register_processor: exception=%s, stacktrace=%s',
                         err,
                         traceback.format_exc())
