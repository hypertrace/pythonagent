import yaml
import os
import json
import logging
from google.protobuf import json_format as jf
from google.protobuf.wrappers_pb2 import BoolValue
from config import config_pb2 as config_pb2



logger = logging.getLogger(__name__)

DEFAULT_OPA_ENDPOINT = "http://opa.traceableai:8181/"
DEFAULT_OPA_POLL_PERIOD_SECONDS = 30
DEFAULT_BODY_MAX_SIZE_BYTES = 128 * 1024

JAVA_AGENT_PATH = "JAVA AGENT SOME PATH"
AGENT_CONFIG_ENABLED = True

class HypertraceConfig:
    def __init__(self, configPath):
        self.configPath = configPath
        self.configs_list = None
        self.loadConfig();

    # Returns a AgentConfig object which contains the configuration from agent-config.yaml
    def loadConfig(self):
        try:
            with open(os.path.join(self.configPath, 'agent-config.yaml')) as file:
                self.configs_list = yaml.load(file, Loader=yaml.FullLoader)
                logger.debug('HypertraceConfig using %s/agent-config.yaml\n%s', self.configPath, json.dumps(self.configs_list, indent=4));

                self.SERVICE_NAME = self.configs_list['service_name']

                self.DATA_CAPTURE_HTTP_BODY_REQUEST = self.configs_list['data_capture']['http_body']['request']
                self.DATA_CAPTURE_HTTP_BODY_RESPONSE = self.configs_list['data_capture']['http_body']['response']

                self.DATA_CAPTURE_HTTP_HEADERS_REQUEST = self.configs_list['data_capture']['http_headers']['request']
                self.DATA_CAPTURE_HTTP_HEADERS_RESPONSE = self.configs_list['data_capture']['http_headers']['response']

                self.DATA_CAPTURE_RPC_METADATA_REQUEST = self.configs_list['data_capture']['rpc_metadata']['request']
                self.DATA_CAPTURE_RPC_METADATA_RESPONSE = self.configs_list['data_capture']['rpc_metadata']['response']

                self.DATA_CAPTURE_RPC_BODY_REQUEST = self.configs_list['data_capture']['rpc_body']['request']
                self.DATA_CAPTURE_RPC_BODY_RESPONSE = self.configs_list['data_capture']['rpc_body']['request']

                self.REPORTING_ENDPOINT = self.configs_list['reporting']['endpoint']
                self.REPORTING_SECURE = self.configs_list['reporting']['secure']

                opa = jf.Parse(jf.MessageToJson(config_pb2.Opa()), config_pb2.Opa)
                opa.endpoint = 'https://localhost',
                opa.poll_period_seconds = 30,
                opa.enabled = True

                reporting = jf.Parse(jf.MessageToJson(config_pb2.Reporting()), config_pb2.Reporting)
                reporting.endpoint = self.REPORTING_ENDPOINT # 'https://localhost'
                reporting.secure = self.REPORTING_SECURE
                reporting.token = '12345'
                reporting.opa = opa
                reporting.trace_reporter_type = config_pb2.TraceReporterType.OTLP

                rpc_body = config_pb2.Message(request=BoolValue(value=self.DATA_CAPTURE_RPC_BODY_REQUEST), response=BoolValue(value=self.DATA_CAPTURE_RPC_BODY_RESPONSE))
                rpc_metadata = config_pb2.Message(request=BoolValue(value=self.DATA_CAPTURE_RPC_METADATA_REQUEST), response=BoolValue(value=self.DATA_CAPTURE_RPC_METADATA_RESPONSE))
                http_body = config_pb2.Message(request=BoolValue(value=self.DATA_CAPTURE_HTTP_BODY_REQUEST), response=BoolValue(value=self.DATA_CAPTURE_HTTP_BODY_RESPONSE))
                http_headers = config_pb2.Message(request=BoolValue(value=self.DATA_CAPTURE_HTTP_HEADERS_REQUEST), response=BoolValue(value=self.DATA_CAPTURE_HTTP_HEADERS_RESPONSE))

                dataCapture = jf.Parse(jf.MessageToJson(config_pb2.DataCapture()), config_pb2.DataCapture)
                dataCapture.http_headers = http_headers
                dataCapture.http_body = http_body
                dataCapture.rpc_metadata = rpc_metadata
                dataCapture.rpc_body = rpc_body
                dataCapture.body_max_size_bytes = 32000

                javaAgent = jf.Parse(jf.MessageToJson(config_pb2.JavaAgent()), config_pb2.JavaAgent)
                javaAgent.filter_jar_paths = JAVA_AGENT_PATH  #not needed for python

                agent_config = jf.Parse(jf.MessageToJson(config_pb2.AgentConfig()), config_pb2.AgentConfig)
                agent_config.service_name = self.SERVICE_NAME
                agent_config.reporting = reporting
                agent_config.data_capture = dataCapture
                agent_config.propagation_formats = config_pb2.PropagationFormat.TRACECONTEXT
                agent_config.enabled = AGENT_CONFIG_ENABLED
                agent_config.javaagent = javaAgent 
                agent_config.resource_attributes = { 'service_name': self.SERVICE_NAME }

                self.agent_config = agent_config;
        except ImportError:
            logger.error('An error occurred while parsing the agent-config file.')
            raise


