from config.config_pb2 import AgentConfig
import logging
import sys
import os
import traceback
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleExportSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry import trace
from opentelemetry.exporter import jaeger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from config  import HypertraceConfig

logger = logging.getLogger(__name__)

class AgentInit:
  def __init__(self):
    logger.debug('Initializing AgentInit object.')
    logger.debug('Nitin -')
    self._moduleInitialized = {
      "flask": False,
      "grpc:server": False,
      "grpc:client": False,
      "mysql": False,
      "postgresql": False
    }
    try:
      hypertraceConfig = HypertraceConfig.HypertraceConfig();
      global agent_config;
      agent_config = hypertraceConfig.getConfig();
      self._tracerProvider = TracerProvider(
        resource=Resource.create({
            "service.name": agent_config.service_name,
            "service.instance.id": os.getpid(),
        })
      )
      trace.set_tracer_provider(self._tracerProvider)

      self._consoleSpanExporter = ConsoleSpanExporter(service_name=agent_config.service_name)
      self._simpleExportSpanProcessor = SimpleExportSpanProcessor(self._consoleSpanExporter)

      self._jaegerExporter = self.createJaegerExporter()
      self._batchExportSpanProcessor = BatchExportSpanProcessor(self._jaegerExporter)

      trace.get_tracer_provider().add_span_processor(self._simpleExportSpanProcessor)
      trace.get_tracer_provider().add_span_processor(self._batchExportSpanProcessor)
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

  def flaskInit(self, app):
    logger.debug('Calling AgentInit.flaskInit().')
    try:
      from instrumentation.flask import FlaskInstrumentorWrapper
      logger.debug('Dump config inside flaskInit :' + str(agent_config.data_capture.http_body));
      self._moduleInitialized['flask'] = True
      self._flaskInstrumentorWrapper = FlaskInstrumentorWrapper()
      self._flaskInstrumentorWrapper.instrument_app(app)
      self._flaskInstrumentorWrapper.setServiceName(agent_config.service_name)
      self._flaskInstrumentorWrapper.setProcessRequestHeaders(agent_config.data_capture.http_headers)
      self._flaskInstrumentorWrapper.setProcessResponseHeaders(agent_config.data_capture.http_headers)
      self._flaskInstrumentorWrapper.setProcessRequestBody(agent_config.data_capture.http_body)
      self._flaskInstrumentorWrapper.setProcessResponseBody(agent_config.data_capture.http_body)
    except:
      logger.debug('Failed to initialize flask instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]

  def grpcServerInit(self):
    logger.debug('Calling AgentInit.grpcServerInit')
    try:
      from instrumentation.grpc import GrpcInstrumentorServerWrapper,GrpcInstrumentorClientWrapper
      self._moduleInitialized['grpc:server'] = True
      self._grpcInstrumentorServerWrapper = GrpcInstrumentorServerWrapper()
      self._grpcInstrumentorServerWrapper.instrument()
      self._grpcInstrumentorServerWrapper.setProcessRequestHeaders(agent_config.data_capture.http_headers)
      self._grpcInstrumentorServerWrapper.setProcessResponseHeaders(agent_config.data_capture.http_headers)
      self._grpcInstrumentorServerWrapper.setProcessRequestBody(agent_config.data_capture.http_headers)
      self._grpcInstrumentorServerWrapper.setProcessResponseBody(agent_config.data_capture.http_headers)
    except:
      logger.debug('Failed to initialize grpc instrumentation wrapper: exception=%s,stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]

  def grpcClientInit(self):
    logger.debug('Calling AgentInit.grpcClientInit')
    try:
      from instrumentation.grpc import GrpcInstrumentorServerWrapper,GrpcInstrumentorClientWrapper
      self._moduleInitialized['grpc:client'] = True
      self._grpcInstrumentorClientWrapper = GrpcInstrumentorClientWrapper()
      self._grpcInstrumentorClientWrapper.instrument()
      self._grpcInstrumentorClientWrapper.setProcessRequestHeaders(agent_config.data_capture.http_headers)
      self._grpcInstrumentorClientWrapper.setProcessResponseHeaders(agent_config.data_capture.http_headers)
      self._grpcInstrumentorClientWrapper.setProcessRequestBody(agent_config.data_capture.http_headers)
      self._grpcInstrumentorClientWrapper.setProcessResponseBody(agent_config.data_capture.http_headers)
    except:
      logger.debug('Failed to initialize grpc instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]


  def mySQLInit(self):
    logger.debug('Calling AgentInit.mysqlInit()')
    try:
      from instrumentation.mysql import MySQLInstrumentorWrapper
      self._moduleInitialized['mysql'] = True
      self._mysqlInstrumentorWrapper = MySQLInstrumentorWrapper() 
      self._mysqlInstrumentorWrapper.instrument()
      self._mysqlInstrumentorWrapper.setProcessRequestHeaders(agent_config.data_capture.http_headers)
      self._mysqlInstrumentorWrapper.setProcessResponseHeaders(agent_config.data_capture.http_headers)
      self._mysqlInstrumentorWrapper.setProcessRequestBody(agent_config.data_capture.http_headers)
      self._mysqlInstrumentorWrapper.setProcessResponseBody(agent_config.data_capture.http_headers)
    except:
      logger.debug('Failed to initialize grpc instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]

  def postgreSQLInit(self):
    logger.debug('Calling AgentInit.postgreSQLInit()')
    try:
      from instrumentation.postgresql import PostgreSQLInstrumentorWrapper
      self._moduleInitialized['postgresql'] = True
      self._postgresqlInstrumentorWrapper = PostgreSQLInstrumentorWrapper()
      self._postgresqlInstrumentorWrapper.instrument()
      self._postgresqlInstrumentorWrapper.setProcessRequestHeaders(agent_config.data_capture.http_headers)
      self._postgresqlInstrumentorWrapper.setProcessResponseHeaders(agent_config.data_capture.http_headers)
      self._postgresqlInstrumentorWrapper.setProcessRequestBody(agent_config.data_capture.http_headers)
      self._postgresqlInstrumentorWrapper.setProcessResponseBody(agent_config.data_capture.http_headers)
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

  def createJaegerExporter(self):
    jaeger_exporter = jaeger.JaegerSpanExporter(
      service_name= agent_config.service_name,
      # configure agent
      agent_host_name='localhost',
      agent_port=6831,
      # optional: configure also collector
      # collector_endpoint='http://localhost:14268/api/traces?format=jaeger.thrift',
      # username=xxxx, # optional
      # password=xxxx, # optional
      # insecure=True, # optional
      # credentials=xxx # optional channel creds
      # transport_format='protobuf' # optional
    )
    return jaeger_exporter
