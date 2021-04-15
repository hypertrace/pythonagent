import os
import yaml
import logging
from google.protobuf import json_format as jf
from google.protobuf.wrappers_pb2 import BoolValue
from hypertrace.agent.config import config_pb2 as config_pb2
from hypertrace.agent.config.AgentConfig_default import *

# Initialize logger
logger = logging.getLogger(__name__)

# Read agent-config file and override with environment variables as necessaary
class AgentConfig:
  def __init__(self):
    """
    Returns a new instance of config_pb2.AgentConfig when a new AgentConfig() is created.
    If 'AGENT_YAML' is specified in the environment data would be loaded from that file.
    If not, data would be loaded from 'DEFAULT_AGENT_CONFIG' on 'AgentConfig_default.py'
    """

    self.config = DEFAULT_AGENT_CONFIG
    self.new_config = None
    if 'AGENT_YAML' in os.environ:
      path = os.path.abspath(os.environ['AGENT_YAML'])
      logger.debug("AgentConfig - using file from %s", path)
      file = open(path, 'r')
      self.new_config = yaml.load(file, Loader=yaml.FullLoader)
      print(self.new_config)

      file.close()
    else:
      logger.debug("AgentConfig - using default")

    if self.new_config:
      for parentKey in DEFAULT_AGENT_CONFIG.keys():
        if parentKey in self.new_config:
            if type(DEFAULT_AGENT_CONFIG[parentKey]) is dict:
                for subKey in DEFAULT_AGENT_CONFIG[parentKey].keys():
                    if subKey in self.new_config[parentKey]:
                        if type(DEFAULT_AGENT_CONFIG[parentKey][subKey]) is dict:
                            for valueKey in DEFAULT_AGENT_CONFIG[parentKey][subKey].keys():
                                if valueKey in self.new_config[parentKey][subKey]:
                                    value = self.new_config[parentKey][subKey][valueKey]
                                    self.config[parentKey][subKey][valueKey] = value
                                    logger.debug("[YAML] %s.%s.%s -> %s", parentKey, subKey, valueKey, value)
                                else:
                                    value = DEFAULT_AGENT_CONFIG[parentKey][subKey][valueKey]
                                    self.config[parentKey][subKey][valueKey] = value
                                    logger.debug("[DEFAULT] %s.%s.%s -> %s", parentKey, subKey, valueKey, value)
                        else:
                            value = self.new_config[parentKey][subKey]
                            logger.debug("[YAML] %s.%s -> %s", parentKey, subKey, value)
                            self.config[parentKey][subKey] = value
                    else:
                        value = DEFAULT_AGENT_CONFIG[parentKey][subKey]
                        self.config[parentKey][subKey] = value
                        logger.debug("[DEFAULT] %s.%s -> %s", parentKey, subKey, value)
            else:
                value = self.new_config[parentKey]
                self.config[parentKey] = value
                logger.debug("[YAML] %s -> %s", parentKey, value)
        else:
            value = DEFAULT_AGENT_CONFIG[parentKey]
            self.config[parentKey] = value
            logger.debug("[DEFAULT] %s -> %s", parentKey, value)

    reporting_token = DEFAULT_REPORTING_TOKEN
    opa_endpoint = DEFAULT_OPA_ENDPOINT
    opa_poll_period_seconds = DEFAULT_OPA_POLL_PERIOD_SECONDS
    opa_enabled = DEFAULT_OPA_ENABLED
    data_capture_max_size_bytes = DEFAULT_DATA_CAPTURE_MAX_SIZE_BYTES
    agent_config_enabled = DEFAULT_AGENT_CONFIG_ENABLED

    # Use variables from environment:
    if 'HT_SERVICE_NAME' in os.environ:
        logger.debug("[env] Loaded HT_SERVICE_NAME from env")
        self.config['service_name'] = os.environ['HT_SERVICE_NAME']

    if 'HT_REPORTING_ENDPOINT' in os.environ:
        logger.debug("[env] Loaded HT_REPORTING_ENDPOINT from env")
        self.config['reporting']['endpoint'] = os.environ['HT_REPORTING_ENDPOINT']

    if 'HT_REPORTING_SECURE' in os.environ:
        logger.debug("[env] Loaded HT_REPORTING_SECURE from env")
        self.config['reporting']['secure'] = os.environ['HT_REPORTING_SECURE'].lower() == 'true'

    if 'HT_REPORTING_TOKEN' in os.environ:
        logger.debug("[env] Loaded HT_REPORTING_TOKEN from env")
        reporting_token = os.environ['HT_REPORTING_TOKEN']

    if 'HT_REPORTING_OPA_ENDPOINT' in os.environ:
        logger.debug("[env] Loaded HT_REPORTING_OPA_ENDPOINT from env")
        opa_endpoint = os.environ['HT_REPORTING_OPA_ENDPOINT']

    if 'HT_REPORTING_OPA_POLL_PERIOD_SECONDS' in os.environ:
        logger.debug("[env] Loaded HT_REPORTING_OPA_POLL_PERIOD_SECONDS from env")
        opa_poll_period_seconds = os.environ['HT_REPORTING_OPA_POLL_PERIOD_SECONDS']

    if 'HT_REPORTING_OPA_ENABLED' in os.environ:
        logger.debug("[env] Loaded HT_REPORTING_OPA_ENABLED from env")
        opa_enabled = os.environ['HT_REPORTING_OPA_ENABLED'].lower() == 'true'

    if 'HT_DATA_CAPTURE_HTTP_HEADERS_REQUEST' in os.environ:
        logger.debug("[env] Loaded HT_DATA_CAPTURE_HTTP_HEADERS_REQUEST from env")
        self.config['data_capture']['http_headers']['request'] = os.environ['HT_DATA_CAPTURE_HTTP_HEADERS_REQUEST'].lower() == 'true'

    if 'HT_DATA_CAPTURE_HTTP_HEADERS_RESPONSE' in os.environ:
        logger.debug("[env] Loaded HT_DATA_CAPTURE_HTTP_HEADERS_RESPONSE from env")
        self.config['data_capture']['http_headers']['response'] = os.environ['HT_DATA_CAPTURE_HTTP_HEADERS_RESPONSE'].lower() == 'true'

    if 'HT_DATA_CAPTURE_HTTP_BODY_REQUEST' in os.environ:
        logger.debug("[env] Loaded HT_DATA_CAPTURE_HTTP_BODY_REQUEST from env")
        self.config['data_capture']['http_body']['request'] = os.environ['HT_DATA_CAPTURE_HTTP_BODY_REQUEST'].lower() == 'true'

    if 'HT_DATA_CAPTURE_HTTP_BODY_RESPONSE' in os.environ:
        logger.debug("[env] Loaded HT_DATA_CAPTURE_HTTP_BODY_RESPONSE from env")
        self.config['data_capture']['http_body']['response'] = os.environ['HT_DATA_CAPTURE_HTTP_BODY_RESPONSE'].lower() == 'true'

    if 'HT_DATA_CAPTURE_RPC_METADATA_REQUEST' in os.environ:
        logger.debug("[env] Loaded HT_DATA_CAPTURE_RPC_METADATA_REQUEST from env")
        self.config['data_capture']['rpc_metadata']['request'] = os.environ['HT_DATA_CAPTURE_RPC_METADATA_REQUEST'].lower() == 'true'

    if 'HT_DATA_CAPTURE_RPC_METADATA_RESPONSE' in os.environ:
        logger.debug("[env] Loaded HT_DATA_CAPTURE_RPC_METADATA_RESPONSE from env")
        self.config['data_capture']['rpc_metadata']['response'] = os.environ['HT_DATA_CAPTURE_RPC_METADATA_RESPONSE'].lower() == 'true'

    if 'HT_DATA_CAPTURE_RPC_BODY_REQUEST' in os.environ:
        logger.debug("[env] Loaded HT_DATA_CAPTURE_RPC_BODY_REQUEST from env")
        self.config['data_capture']['rpc_body']['request'] = os.environ['HT_DATA_CAPTURE_RPC_BODY_REQUEST'].lower() == 'true'

    if 'HT_DATA_CAPTURE_RPC_BODY_RESPONSE' in os.environ:
        logger.debug("[env] Loaded HT_DATA_CAPTURE_RPC_BODY_RESPONSE from env")
        self.config['data_capture']['rpc_body']['response'] = os.environ['HT_DATA_CAPTURE_RPC_BODY_RESPONSE'].lower() == 'true'

    if 'HT_DATA_CAPTURE_BODY_MAX_SIZE_BYTES' in os.environ:
        logger.debug("[env] Loaded HT_DATA_CAPTURE_BODY_MAX_SIZE_BYTES from env")
        data_capture_max_size_bytes = os.environ['HT_DATA_CAPTURE_BODY_MAX_SIZE_BYTES']

    # if 'HT_PROPAGATION_FORMATS' in os.environ:
    #     logger.debug("[env] Loaded HT_PROPAGATION_FORMATS from env")
    #     self.config[''] = os.environ['HT_PROPAGATION_FORMATS']

    if 'HT_ENABLED' in os.environ:
        logger.debug("[env] Loaded HT_ENABLED from env")
        agent_config_enabled = os.environ['HT_ENABLED'].lower() == 'true'

    self.opa = jf.Parse(jf.MessageToJson(config_pb2.Opa()), config_pb2.Opa)
    self.opa.endpoint = opa_endpoint
    self.opa.poll_period_seconds = opa_poll_period_seconds
    self.opa.enabled = opa_enabled

    self.reporting = jf.Parse(jf.MessageToJson(config_pb2.Reporting()), config_pb2.Reporting)
    self.reporting.endpoint = self.config['reporting']['endpoint']  # 'https://localhost'
    self.reporting.secure = self.config['reporting']['secure']
    self.reporting.token = reporting_token
    self.reporting.opa = self.opa
    self.reporting.trace_reporter_type = config_pb2.TraceReporterType.OTLP

    self.rpc_body = config_pb2.Message(request=BoolValue(value=self.config['data_capture']['rpc_body']['request']),
                                       response=BoolValue(value=self.config['data_capture']['rpc_body']['response']))
    self.rpc_metadata = config_pb2.Message(request=BoolValue(value=self.config['data_capture']['rpc_metadata']['request']),
                                           response=BoolValue(value=self.config['data_capture']['rpc_metadata']['response']))
    self.http_body = config_pb2.Message(request=BoolValue(value=self.config['data_capture']['http_body']['request']),
                                        response=BoolValue(value=self.config['data_capture']['http_body']['response']))
    self.http_headers = config_pb2.Message(request=BoolValue(value=self.config['data_capture']['http_headers']['request']),
                                           response=BoolValue(value=self.config['data_capture']['http_headers']['response']))

    self.data_capture = jf.Parse(jf.MessageToJson(config_pb2.DataCapture()), config_pb2.DataCapture)
    self.data_capture.http_headers = self.http_headers
    self.data_capture.http_body = self.http_body
    self.data_capture.rpc_metadata = self.rpc_metadata
    self.data_capture.rpc_body = self.rpc_body
    self.data_capture.body_max_size_bytes = data_capture_max_size_bytes

    self.agent_config = jf.Parse(jf.MessageToJson(config_pb2.AgentConfig()), config_pb2.AgentConfig)
    self.agent_config.service_name = self.config['service_name']
    self.agent_config.reporting = self.reporting
    self.agent_config.data_capture = self.data_capture
    self.agent_config.propagation_formats = config_pb2.PropagationFormat.TRACECONTEXT
    self.agent_config.enabled = agent_config_enabled
    self.agent_config.resource_attributes = {'service_name': self.config['service_name']}

    self.service_name = self.config['service_name']

  def dumpConfig(self):
    logger.info(self.__dict__)
