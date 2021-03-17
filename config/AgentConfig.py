import config_pb2 as config_pb2
import yaml
import traceback
from google.protobuf import json_format as jf

import logging

logger = logging.getLogger(__name__)
class HypertraceConfig:  
    DEFAULT_OPA_ENDPOINT = "http://opa.traceableai:8181/";
    DEFAULT_OPA_POLL_PERIOD_SECONDS = 30;
    DEFAULT_BODY_MAX_SIZE_BYTES = 128 * 1024
    REPORTING_ENDPOINT= "http://localhost:9411/api/v2/spans" ;
    REPORTING_SECURE = False ;
    DATA_CAPTURE_HTTP_HEADERS_REQUEST = True ;
    DATA_CAPTURE_HTTP_HEADERS_RESPONSE =  True  ; 
    DATA_CAPTURE_HTTP_BODY_REQUEST = True ;
    DATA_CAPTURE_HTTP_BODY_RESPONSE = True ;
    DATA_CAPTURE_RPC_METADATA_REQUEST = True ;
    DATA_CAPTURE_RPC_METADATA_RESPONSE  = True ;
    DATA_CAPTURE_RPC_BODY_REQUEST = True ;
    DATA_CAPTURE_RPC_BODY_RESPONSE = True ;
    SERVICE_NAME = "DemoService"

    def __init__(self):  
      try:
        from configparser import ConfigParser
        
        with open('../config/agent-config.yaml') as file:
          configs_list = yaml.load(file, Loader=yaml.FullLoader)
          self.DATA_CAPTURE_HTTP_HEADERS_REQUEST = configs_list['data_capture']['http_headers']['request'];
          self.DATA_CAPTURE_HTTP_HEADERS_RESPONSE = configs_list['data_capture']['http_headers']['response'];
          self.DATA_CAPTURE_HTTP_BODY_REQUEST = configs_list['data_capture']['http_body']['request'];
          self.DATA_CAPTURE_HTTP_BODY_REQUEST = configs_list['data_capture']['http_body']['response'];
          self.DATA_CAPTURE_RPC_METADATA_REQUEST = configs_list['data_capture']['rpc_metadata']['request'];
          self.DATA_CAPTURE_RPC_METADATA_RESPONSE = configs_list['data_capture']['rpc_metadata']['response'];
          self.DATA_CAPTURE_RPC_BODY_REQUEST = configs_list['data_capture']['rpc_body']['request'];
          self.DATA_CAPTURE_RPC_BODY_RESPONSE = configs_list['data_capture']['rpc_body']['response'];
    
      except ImportError:
        logger.error('An error occurred while parsing the agent-config file: exception=%s, stacktrace=%s', sys.exc_info()[0], traceback.format_exc())
        from ConfigParser import ConfigParser  # ver. < 3.0

aHypertraceConfig = HypertraceConfig();
opa = jf.Parse(jf.MessageToJson(config_pb2.Opa()), config_pb2.Opa)
opa.endpoint = aHypertraceConfig.DEFAULT_OPA_ENDPOINT,
opa.poll_period_seconds = 30,
opa.enabled = True

reporting = jf.Parse(jf.MessageToJson(config_pb2.Reporting()), config_pb2.Reporting)
reporting.endpoint = 'https://localhost'
reporting.secure = True,
reporting.token = '12345'
reporting.opa = opa
reporting.trace_reporter_type = config_pb2.TraceReporterType.OTLP

message = jf.Parse(jf.MessageToJson(config_pb2.Message()), config_pb2.Message)
message.request = aHypertraceConfig.DATA_CAPTURE_HTTP_BODY_REQUEST
message.response = aHypertraceConfig.DATA_CAPTURE_HTTP_BODY_RESPONSE 

dataCapture = jf.Parse(jf.MessageToJson(config_pb2.DataCapture()), config_pb2.DataCapture)
dataCapture.http_headers = message
dataCapture.http_body = message
dataCapture.rpc_metadata = message
dataCapture.rpc_body = message
dataCapture.body_max_size_bytes = 32000

javaAgent = jf.Parse(jf.MessageToJson(config_pb2.JavaAgent()), config_pb2.JavaAgent)
javaAgent.filter_jar_paths = 'some_path:.' #not needed for python

agent_config = jf.Parse(jf.MessageToJson(config_pb2.AgentConfig()), config_pb2.AgentConfig)
agent_config.service_name = aHypertraceConfig.SERVICE_NAME
agent_config.reporting = reporting
agent_config.data_capture = dataCapture
agent_config.propagation_formats = config_pb2.PropagationFormat.TRACECONTEXT
agent_config.enabled = True
agent_config.javaagent = javaAgent
agent_config.resource_attributes = { 'service_name': aHypertraceConfig.SERVICE_NAME }

print(agent_config.service_name)
print(agent_config.reporting.endpoint)
print(agent_config.javaagent.filter_jar_paths)
