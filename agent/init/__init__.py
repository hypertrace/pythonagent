import sys
import os
import traceback
import logging
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
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
      "postgresql": False
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

      self._requestsInstrumentor = RequestsInstrumentor()

      self._flaskInstrumentorWrapper = None
      self._grpcInstrumentorClientWrapper = None
      self._grpcInstrumentorServerWrapper = None
      self._mysqlInstrumentorWrapper = None
      self._postgresqlInstrumentorWrapper = None
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
  def flaskInit(self, app):
    logger.debug('Calling AgentInit.flaskInit().')
    try:
      from agent.instrumentation.flask import FlaskInstrumentorWrapper
      self._moduleInitialized['flask'] = True
      self._flaskInstrumentorWrapper = FlaskInstrumentorWrapper()
      self._flaskInstrumentorWrapper.instrument_app(app)
      self._flaskInstrumentorWrapper.setServiceName(self._agent._config.service_name)

      self._flaskInstrumentorWrapper.setProcessRequestHeaders(self._agent._config.data_capture.http_headers.request)
      self._flaskInstrumentorWrapper.setProcessRequestBody(self._agent._config.data_capture.http_body.request)

      self._flaskInstrumentorWrapper.setProcessResponseHeaders(self._agent._config.data_capture.http_headers.response)
      self._flaskInstrumentorWrapper.setProcessResponseBody(self._agent._config.data_capture.http_body.response)
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
      self._mysqlInstrumentorWrapper.instrument()

      self._mysqlInstrumentorWrapper.setProcessRequestHeaders(self._agent._config.data_capture.http_headers.request)
      self._mysqlInstrumentorWrapper.setProcessRequestBody(self._agent._config.data_capture.http_body.request)

      self._mysqlInstrumentorWrapper.setProcessResponseHeaders(self._agent._config.data_capture.http_headers.response)
      self._mysqlInstrumentorWrapper.setProcessResponseBody(self._agent._config.data_capture.http_body.response)

    except:
      logger.debug('Failed to initialize grpc instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]

  # Creates a postgresql server wrapper using the config defined in hypertraceconfig
  def postgreSQLInit(self):
    logger.debug('Calling AgentInit.postgreSQLInit()')
    try:
      from agent.instrumentation.postgresql import PostgreSQLInstrumentorWrapper
      self._moduleInitialized['postgresql'] = True
      self._postgresqlInstrumentorWrapper = PostgreSQLInstrumentorWrapper()
      self._postgresqlInstrumentorWrapper.instrument()

      self._postgresqlInstrumentorWrapper.setProcessRequestHeaders(self._agent._config.data_capture.http_headers.request)
      self._postgresqlInstrumentorWrapper.setProcessRequestBody(self._agent._config.data_capture.http_body.request)

      self._postgresqlInstrumentorWrapper.setProcessResponseHeaders(self._agent._config.data_capture.http_headers.response)
      self._postgresqlInstrumentorWrapper.setProcessResponseBody(self._agent._config.data_capture.http_body.response)
    except:
      logger.debug('Failed to initialize grpc instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]

  def globalInit(self):
    logger.debug('Calling AgentInit.globalInit().')
    try:
      self._requestsInstrumentor.instrument()
    except:
      logger.debug('Failed global init: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]

  def globalDisable(self):
    logger.debug('Calling AgentInit.globalDisable().')
    try:
      self._requestsInstrumentor.uninstrument()
    except:
      logger.debug('Failed global init: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]

  def setProcessor(self, processor):
    logger.debug('Entering AgentInit.setProcessor().')
    trace.get_tracer_provider().add_span_processor(processor)
