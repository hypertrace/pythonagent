import sys
import os
import traceback
import logging
import json
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.exporter.zipkin.proto.http import ZipkinExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace import TracerProvider, export
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from agent.config import AgentConfig

# Initialize logger
logger = logging.getLogger(__name__)

class AgentInit:
  def __init__(self, agent):
    logger.debug('Initializing AgentInit object.')
    self._agent = agent
    self._config = agent._config;
    self._moduleInitialized = {
      "flask": False,
      "grpc:server": False,
      "grpc:client": False,
      "mysql": False,
      "postgresql": False, 
      "requests": False
    }
    try:
      self._config.dumpConfig()

      self._tracerProvider = TracerProvider(
        resource=Resource.create({
            "service.name": self._config.service_name,
            "service.instance.id": os.getpid(),
        })
      )
      trace.set_tracer_provider(self._tracerProvider)

      self._consoleSpanExporter = ConsoleSpanExporter(service_name=self._agent._config.service_name)
      self._simpleExportSpanProcessor = SimpleSpanProcessor(self._consoleSpanExporter)

      trace.get_tracer_provider().add_span_processor(self._simpleExportSpanProcessor)

      self.setZipkinProcessor()

      self._flaskInstrumentorWrapper = None
      self._grpcInstrumentorClientWrapper = None
      self._grpcInstrumentorServerWrapper = None
      self._mysqlInstrumentorWrapper = None
      self._postgresqlInstrumentorWrapper = None
      self._requestsInstrumentorWrapper = None
    except:
      logger.error('Failed to initialize opentelemetry: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]

  def dumpConfig(self):
    logger.debug('Calling DumpConfig().')
    for m in self._moduleInitialized:
      logger.debug(m + ':' + str(self._moduleInitialized[m]))

  # Creates a flask wrapper using the config defined in hypertraceconfig
  def flaskInit(self, app, useB3=False):
    logger.debug('Calling AgentInit.flaskInit().')
    try:
      from agent.instrumentation.flask import FlaskInstrumentorWrapper
      self._moduleInitialized['flask'] = True
      self._flaskInstrumentorWrapper = FlaskInstrumentorWrapper()
      self._flaskInstrumentorWrapper.instrument_app(app)
      self.initInstrumentorWrapperBaseForHTTP(self._flaskInstrumentorWrapper)
      if useB3:
        from opentelemetry.propagate import set_global_textmap
        from opentelemetry.propagators.b3 import B3Format
        set_global_textmap(B3Format())
    except:
      logger.debug('Failed to initialize flask instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]

  # Creates a grpc server wrapper using the config defined in hypertraceconfig
  def grpcServerInit(self):
    logger.debug('Calling AgentInit.grpcServerInit')
    try:
      from agent.instrumentation.grpc import GrpcInstrumentorServerWrapper,GrpcInstrumentorClientWrapper
      self._moduleInitialized['grpc:server'] = True
      self._grpcInstrumentorServerWrapper = GrpcInstrumentorServerWrapper()
      self._grpcInstrumentorServerWrapper.instrument()

      self._grpcInstrumentorServerWrapper.setProcessRequestHeaders(self._agent._config.data_capture.http_headers.request)
      self._grpcInstrumentorServerWrapper.setProcessRequestBody(self._agent._config.data_capture.http_body.request)

      self._grpcInstrumentorServerWrapper.setProcessResponseHeaders(self._agent._config.data_capture.http_headers.response)
      self._grpcInstrumentorServerWrapper.setProcessResponseBody(self._agent._config.data_capture.http_body.response)
    except:
      logger.debug('Failed to initialize grpc instrumentation wrapper: exception=%s,stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]

  # Creates a grpc client wrapper using the config defined in hypertraceconfig
  def grpcClientInit(self):
    logger.debug('Calling AgentInit.grpcClientInit')
    try:
      from agent.instrumentation.grpc import GrpcInstrumentorServerWrapper,GrpcInstrumentorClientWrapper
      self._moduleInitialized['grpc:client'] = True

      self._grpcInstrumentorClientWrapper = GrpcInstrumentorClientWrapper()
      self._grpcInstrumentorClientWrapper.instrument()

      self._grpcInstrumentorClientWrapper.setProcessRequestHeaders(self._agent._config.data_capture.http_headers.request)
      self._grpcInstrumentorClientWrapper.setProcessRequestBody(self._agent._config.data_capture.http_body.request)

      self._grpcInstrumentorClientWrapper.setProcessResponseHeaders(self._agent._config.data_capture.http_headers.response)
      self._grpcInstrumentorClientWrapper.setProcessResponseBody(self._agent._config.data_capture.http_body.response)
    except:
      logger.debug('Failed to initialize grpc instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]


  # Creates a mysql server wrapper using the config defined in hypertraceconfig
  def mySQLInit(self):
    logger.debug('Calling AgentInit.mysqlInit()')
    try:
      from agent.instrumentation.mysql import MySQLInstrumentorWrapper
      self._moduleInitialized['mysql'] = True
      self._mysqlInstrumentorWrapper = MySQLInstrumentorWrapper()
      self.initInstrumentorWrapperBaseForHTTP(self._mysqlInstrumentorWrapper)
    except:
      logger.debug('Failed to initialize mysql instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]

  # Creates a postgresql client wrapper using the config defined in hypertraceconfig
  def postgreSQLInit(self):
    logger.debug('Calling AgentInit.postgreSQLInit()')
    try:
      from agent.instrumentation.postgresql import PostgreSQLInstrumentorWrapper
      self._moduleInitialized['postgresql'] = True
      self._postgresqlInstrumentorWrapper = PostgreSQLInstrumentorWrapper()
      self.initInstrumentorWrapperBaseForHTTP(self._postgresqlInstrumentorWrapper)
    except:
      logger.debug('Failed to initialize postgresql instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]

  # Creates a requests client wrapper using the config defined in hypertraceconfig
  def requestsInit(self, useB3=False):
    logger.debug('Calling AgentInit.requestsInit()')
    try:
      from agent.instrumentation.requests import RequestsInstrumentorWrapper
      self._moduleInitialized['requests'] = True
      self._requestsInstrumentorWrapper = RequestsInstrumentorWrapper()
      self.initInstrumentorWrapperBaseForHTTP(self._requestsInstrumentorWrapper)
      if useB3:
        from opentelemetry.propagate import set_global_textmap
        from opentelemetry.propagators.b3 import B3Format
        set_global_textmap(B3Format())
    except:
      logger.debug('Failed to initialize requests instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]

  def initInstrumentorWrapperBaseForHTTP(self, instrumentor):
    logger.debug('Calling AgentInit.initInstrumentorWrapperBaseForHTTP().')
    instrumentor.instrument()

    instrumentor.setProcessRequestHeaders(self._agent._config.data_capture.http_headers.request)
    instrumentor.setProcessRequestBody(self._agent._config.data_capture.http_body.request)

    instrumentor.setProcessResponseHeaders(self._agent._config.data_capture.http_headers.response)
    instrumentor.setProcessResponseBody(self._agent._config.data_capture.http_body.response)

  def setProcessor(self, processor):
    logger.debug('Entering AgentInit.setProcessor().')
    trace.get_tracer_provider().add_span_processor(processor)


  def setZipkinProcessor(self):
    if 'OTEL_TRACES_EXPORTER' in os.environ:
      if os.environ['OTEL_TRACES_EXPORTER'] == 'zipkin':
        logger.debug("OTEL_TRACES_EXPORTER is zipkin, adding exporter.")
      else:
        return
    else:
        return

    try:
      zipkin_exporter = ZipkinExporter(
      # version=Protocol.V2
      # optional:
      # endpoint set to agent-config.yaml reporting endpoint
      endpoint=self._agent._config.reporting.endpoint,
      # local_node_ipv4="192.168.0.1",
      # local_node_ipv6="2001:db8::c001",
      # local_node_port=31313,
      # max_tag_value_length=256
      )

      span_processor = BatchSpanProcessor(zipkin_exporter)
      trace.get_tracer_provider().add_span_processor(span_processor)

      logger.info('Added ZipkinExporter span exporter')
    except:
      logger.error('Failed to setProcessor: exception=%s, stacktrace=%s',
      sys.exc_info()[0],
      traceback.format_exc())
