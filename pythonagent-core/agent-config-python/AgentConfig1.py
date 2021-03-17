import yaml
import config_pb2 as config_pb2
from google.protobuf import json_format as jf

import logging
logger = logging.getLogger(__name__)
DEFAULT_OPA_ENDPOINT = "http://opa.traceableai:8181/";
DEFAULT_OPA_POLL_PERIOD_SECONDS = 30;
DEFAULT_BODY_MAX_SIZE_BYTES = 128 * 1024
REPORTING_ENDPOINT= "http://localhost:9411/api/v2/spans" ;
SERVICE_NAME= "Service Name"
REPORTING_SECURE = False ;
AGENT_CONFIG_ENABLED = True;
JAVA_AGENT_PATH = "JAVA AGENT SOME PATH"
DATA_CAPTURE_HTTP_HEADERS_REQUEST = True ;
DATA_CAPTURE_HTTP_HEADERS_RESPONSE =  True  ; 
DATA_CAPTURE_HTTP_BODY_REQUEST = True ;
DATA_CAPTURE_HTTP_BODY_RESPONSE = True ;
DATA_CAPTURE_RPC_METADATA_REQUEST = True ;
DATA_CAPTURE_RPC_METADATA_RESPONSE  = True ;
DATA_CAPTURE_RPC_BODY_REQUEST = True ;
DATA_CAPTURE_RPC_BODY_RESPONSE = True ;

class HypertraceConfig:  
    

    def __init__(self):  
            
      try:
        global JAVA_AGENT_PATH 
        global  DEFAULT_OPA_ENDPOINT 
        global  DEFAULT_OPA_POLL_PERIOD_SECONDS 
        global  DEFAULT_BODY_MAX_SIZE_BYTES 
        global  REPORTING_ENDPOINT
        global  SERVICE_NAME
        global  REPORTING_SECURE
        global  AGENT_CONFIG_ENABLED
        global  JAVA_AGENT_PATH
        global  DATA_CAPTURE_HTTP_HEADERS_REQUEST
        global  DATA_CAPTURE_HTTP_HEADERS_RESPONSE
        global  DATA_CAPTURE_HTTP_BODY_REQUEST
        global  DATA_CAPTURE_HTTP_BODY_RESPONSE
        global  DATA_CAPTURE_RPC_METADATA_REQUEST
        global  DATA_CAPTURE_RPC_METADATA_RESPONSE
        global  DATA_CAPTURE_RPC_BODY_REQUEST
        global  DATA_CAPTURE_RPC_BODY_RESPONSE


        logger.error('Initializing Cofig data from YAML')
        from configparser import ConfigParser
        with open('../../config/agent-config.yaml') as file:
          configs_list = yaml.load(file, Loader=yaml.FullLoader)
          DATA_CAPTURE_HTTP_HEADERS_REQUEST = configs_list['data_capture']['http_headers']['request'];
          DATA_CAPTURE_HTTP_HEADERS_RESPONSE = configs_list['data_capture']['http_headers']['response'];
          DATA_CAPTURE_HTTP_BODY_REQUEST = configs_list['data_capture']['http_body']['request'];
          DATA_CAPTURE_HTTP_BODY_REQUEST = configs_list['data_capture']['http_body']['response'];
          DATA_CAPTURE_RPC_METADATA_REQUEST = configs_list['data_capture']['rpc_metadata']['request'];
          DATA_CAPTURE_RPC_METADATA_RESPONSE = configs_list['data_capture']['rpc_metadata']['response'];
          JAVA_AGENT_PATH = "adadad"
          print(JAVA_AGENT_PATH)
    
      except ImportError:
        logger.error('An error occurred while parsing the agent-config file.')
        from ConfigParser import ConfigParser  # ver. < 3.0

    def getConfig(self):  
        try:
            

            opa = jf.Parse(jf.MessageToJson(config_pb2.Opa()), config_pb2.Opa)
            opa.endpoint = 'https://localhost',
            opa.poll_period_seconds = 30,
            opa.enabled = True

            reporting = jf.Parse(jf.MessageToJson(config_pb2.Reporting()), config_pb2.Reporting)
            reporting.endpoint = 'https://localhost'
            reporting.secure = True,
            reporting.token = '12345'
            reporting.opa = opa
            reporting.trace_reporter_type = config_pb2.TraceReporterType.OTLP

            message = jf.Parse(jf.MessageToJson(config_pb2.Message()), config_pb2.Message)
            message.request = True
            message.response = False

            dc_message = jf.Parse(jf.MessageToJson(config_pb2.Message()), config_pb2.Message)
            dc_message.request = DATA_CAPTURE_HTTP_HEADERS_REQUEST
            dc_message.response = DATA_CAPTURE_HTTP_HEADERS_RESPONSE



            dataCapture = jf.Parse(jf.MessageToJson(config_pb2.DataCapture()), config_pb2.DataCapture)
            dataCapture.http_headers = dc_message
            dataCapture.http_body = dc_message
            dataCapture.rpc_metadata = dc_message
            dataCapture.rpc_body = dc_message
            dataCapture.body_max_size_bytes = 32000

            javaAgent = jf.Parse(jf.MessageToJson(config_pb2.JavaAgent()), config_pb2.JavaAgent)
            javaAgent.filter_jar_paths = JAVA_AGENT_PATH  #not needed for python

            agent_config = jf.Parse(jf.MessageToJson(config_pb2.AgentConfig()), config_pb2.AgentConfig)
            agent_config.service_name = SERVICE_NAME
            agent_config.reporting = reporting
            agent_config.data_capture = dataCapture
            agent_config.propagation_formats = config_pb2.PropagationFormat.TRACECONTEXT
            agent_config.enabled = AGENT_CONFIG_ENABLED
            agent_config.javaagent = javaAgent 
            agent_config.resource_attributes = { 'service_name': SERVICE_NAME }

            print(agent_config.service_name)
            print(agent_config.reporting.endpoint)
            print(agent_config.javaagent.filter_jar_paths)
        except ImportError:
            logger.error('An error occurred while parsing the agent-config file.')

aHypertraceConfig = HypertraceConfig();
aHypertraceConfig.getConfig();


