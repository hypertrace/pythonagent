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
from opentelemetry.exporter import jaeger
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
    self.agent = agent 
    self._moduleInitialized = {
      "flask": False,
      "grpc:server": False,
      "grpc:client": False,
      "mysql": False,
      "postgresql": False
    }
    try:
      logger.debug('http_headers -> request: ' + str(self.agent.config.data_capture.http_headers.request.value))
      logger.debug('http_headers -> response: ' + str(self.agent.config.data_capture.http_headers.response.value))
      logger.debug('http_body -> request: ' + str(self.agent.config.data_capture.http_body.request.value))
      logger.debug('http_body -> response: ' + str(self.agent.config.data_capture.http_body.response.value))
      logger.debug('rpc_body -> request: ' + str(self.agent.config.data_capture.rpc_body.request.value))
      logger.debug('rpc_body -> response: ' + str(self.agent.config.data_capture.rpc_body.response.value))
      logger.debug('rpc_metadata -> request: ' + str(self.agent.config.data_capture.rpc_metadata.request.value))
      logger.debug('rpc_metadata -> response: ' + str(self.agent.config.data_capture.rpc_metadata.response.value))

      self._tracerProvider = TracerProvider(
        resource=Resource.create({
            "service.name": self.agent.config.service_name,
            "service.instance.id": os.getpid(),
        })
      )
      trace.set_tracer_provider(self._tracerProvider)

      self._consoleSpanExporter = ConsoleSpanExporter(service_name=self.agent.config.service_name)
      self._simpleExportSpanProcessor = SimpleSpanProcessor(self._consoleSpanExporter)

#      self.createJaegerExporter()

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
      self._flaskInstrumentorWrapper.setServiceName(self.agent.config.service_name)

      self._flaskInstrumentorWrapper.setProcessRequestHeaders(self.agent.config.data_capture.http_headers.request)
      self._flaskInstrumentorWrapper.setProcessRequestBody(self.agent.config.data_capture.http_body.request)

      self._flaskInstrumentorWrapper.setProcessResponseHeaders(self.agent.config.data_capture.http_headers.response)
      self._flaskInstrumentorWrapper.setProcessResponseBody(self.agent.config.data_capture.http_body.response)
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

      self._grpcInstrumentorServerWrapper.setProcessRequestHeaders(self.agent.config.data_capture.http_headers.request)
      self._grpcInstrumentorServerWrapper.setProcessRequestBody(self.agent.config.data_capture.http_body.request)

      self._grpcInstrumentorServerWrapper.setProcessResponseHeaders(self.agent.config.data_capture.http_headers.response)
      self._grpcInstrumentorServerWrapper.setProcessResponseBody(self.agent.config.data_capture.http_body.response)
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

      self._grpcInstrumentorClientWrapper.setProcessRequestHeaders(self.agent.config.data_capture.http_headers.request)
      self._grpcInstrumentorClientWrapper.setProcessRequestBody(self.agent.config.data_capture.http_body.request)

      self._grpcInstrumentorClientWrapper.setProcessResponseHeaders(self.agent.config.data_capture.http_headers.response)
      self._grpcInstrumentorClientWrapper.setProcessResponseBody(self.agent.config.data_capture.http_body.response)
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

      self._mysqlInstrumentorWrapper.setProcessRequestHeaders(self.agent.config.data_capture.http_headers.request)
      self._mysqlInstrumentorWrapper.setProcessRequestBody(self.agent.config.data_capture.http_body.request)

      self._mysqlInstrumentorWrapper.setProcessResponseHeaders(self.agent.config.data_capture.http_headers.response)
      self._mysqlInstrumentorWrapper.setProcessResponseBody(self.agent.config.data_capture.http_body.response)

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

      self._postgresqlInstrumentorWrapper.setProcessRequestHeaders(self.agent.config.data_capture.http_headers.request)
      self._postgresqlInstrumentorWrapper.setProcessRequestBody(self.agent.config.data_capture.http_body.request)

      self._postgresqlInstrumentorWrapper.setProcessResponseHeaders(self.agent.config.data_capture.http_headers.response)
      self._postgresqlInstrumentorWrapper.setProcessResponseBody(self.agent.config.data_capture.http_body.response)
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
    self._jaegerExporter = self.createJaegerExporter()
    self._batchExportSpanProcessor = BatchSpanProcessor(self._jaegerExporter)

    trace.get_tracer_provider().add_span_processor(self._batchExportSpanProcessor)

    return jaeger_exporter

  def getInMemorySpanExport(self):
    return self._memory_exporter

  def setInMemorySpanExport(self,memory_exporter):
    self._memory_exporter = memory_exporter
    self._simpleExportSpanProcessor2 = export.SimpleSpanProcessor(self._memory_exporter)
    trace.get_tracer_provider().add_span_processor(self._simpleExportSpanProcessor2)
