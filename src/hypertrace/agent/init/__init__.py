'''Initialize all the components using configuration from AgentConfig'''
import sys
import os
import traceback
import logging
from typing import Union

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, export
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.exporter.zipkin.proto.http import ZipkinExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.trace import ProxyTracerProvider
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

        # Only available in python > 3.7
        # this does prevent user from having to add post fork hooks to their
        # web server config
        if hasattr(os, 'register_at_fork'):
            logger.info('Registering after_in_child handler.')
            os.register_at_fork(after_in_child=self.post_fork)  # pylint:disable=E1101

        try:
            self.apply_config(None)

        except Exception as err:  # pylint: disable=W0703
            logger.error('Failed to initialize tracer: exception=%s, stacktrace=%s',
                         err,
                         traceback.format_exc())
            raise sys.exc_info()[0]

    def post_fork(self):
        """Used to reinitialize exporter & processors in separate worker processes"""
        self.apply_config(None)  # pylint:disable=W0212

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
        if isinstance(trace.get_tracer_provider(), ProxyTracerProvider):
            logger.debug("no configured trace provider detected, adding one")
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
            tracer_provider = TracerProvider(
                resource=Resource.create(resource_attributes)
            )
            trace.set_tracer_provider(tracer_provider)
        else:
            logger.debug("tracer provider already configured, "
                         "skipping trace provider configuration")

    def init_exporter(self) -> None:
        """Initialize exporter"""
        reporter_type = self._config.agent_config.reporting.trace_reporter_type
        self._init_exporter(reporter_type)

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

    def _set_wrapper_fields(self, wrapper):
        data_cap = self._config.agent_config.data_capture
        wrapper.set_process_request_headers(data_cap.http_headers.request)
        wrapper.set_process_request_body(data_cap.http_body.request)
        wrapper.set_process_response_headers(data_cap.http_headers.response)
        wrapper.set_process_response_body(data_cap.http_body.response)
        wrapper.set_body_max_size(data_cap.body_max_size_bytes)

    def init_library_instrumentation(self, instrumentation_name, wrapper_instance):
        """used to configure instrumentation wrapper settings + apply instrumentation"""
        logger.debug("Attempting to initialize %s instrumentation", instrumentation_name)
        try:
            self._set_wrapper_fields(wrapper_instance)
            wrapper_instance.instrument()
        except Exception as err: # pylint: disable=W0703
            logger.debug(constants.INST_WRAP_EXCEPTION_MSSG,
                         instrumentation_name,
                         err,
                         traceback.format_exc())

    def register_processor(self, processor) -> None:  # pylint:disable=R0201
        '''Register additional span exporter + processor'''
        logger.debug('Entering AgentInit.register_processor().')
        trace.get_tracer_provider().add_span_processor(processor)

    def set_console_span_processor(self) -> None:
        '''Register the console span processor for debugging purposes.'''
        logger.debug('Entering AgentInit.setConsoleSpanProcessor().')
        console_span_exporter = ConsoleSpanExporter(
            service_name=self._config.agent_config.service_name)
        simple_export_span_processor = SimpleSpanProcessor(
            console_span_exporter)
        trace.get_tracer_provider().add_span_processor(simple_export_span_processor)

    def _init_exporter(self, trace_reporter_type):
        try:
            if trace_reporter_type == config_pb2.TraceReporterType.ZIPKIN:
                exporter = ZipkinExporter(
                    endpoint=self._config.agent_config.reporting.endpoint
                )
            elif trace_reporter_type == config_pb2.TraceReporterType.OTLP:
                exporter = OTLPSpanExporter(endpoint=self._config.agent_config.reporting.endpoint,
                                            insecure= not self._config.agent_config.reporting.secure)
            else:
                logger.error("Unknown exporter type `%s`", trace_reporter_type)

            span_processor = BatchSpanProcessor(exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)

            logger.info(
                'Initialized Zipkin exporter reporting to `%s`',
                self._config.agent_config.reporting.endpoint)
        except Exception as err:  # pylint: disable=W0703
            logger.error('Failed to initialize Zipkin exporter: exception=%s, stacktrace=%s',
                         err,
                         traceback.format_exc())
