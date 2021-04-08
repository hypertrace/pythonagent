import os
import yaml
import logging
from google.protobuf import json_format as jf
from google.protobuf.wrappers_pb2 import BoolValue
from agent.config import config_pb2 as config_pb2
from agent.config.AgentConfig_default import *

# Initialize logger
logger = logging.getLogger(__name__)

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

    self.opa = jf.Parse(jf.MessageToJson(config_pb2.Opa()), config_pb2.Opa)
    self.opa.endpoint = DEFAULT_OPA_ENDPOINT,
    self.opa.poll_period_seconds = DEFAULT_OPA_POLL_PERIOD_SECONDS,
    self.opa.enabled = DEFAULT_OPA_ENABLED

    self.reporting = jf.Parse(jf.MessageToJson(config_pb2.Reporting()), config_pb2.Reporting)
    self.reporting.endpoint = os.environ['OTEL_EXPORTER_ZIPKIN_ENDPOINT'] if 'OTEL_EXPORTER_ZIPKIN_ENDPOINT' in os.environ else self.config['reporting']['endpoint']  # 'https://localhost'
    self.reporting.secure = self.config['reporting']['secure']
    self.reporting.token = DEFAULT_REPORTING_TOKEN
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
    self.data_capture.body_max_size_bytes = DEFAULT_DATA_CAPTURE_MAX_SIZE_BYTES

    self.agent_config = jf.Parse(jf.MessageToJson(config_pb2.AgentConfig()), config_pb2.AgentConfig)
    self.agent_config.service_name = self.config['service_name']
    self.agent_config.reporting = self.reporting
    self.agent_config.data_capture = self.data_capture
    self.agent_config.propagation_formats = config_pb2.PropagationFormat.TRACECONTEXT
    self.agent_config.enabled = DEFAULT_AGENT_CONFIG_ENABLED
    self.agent_config.resource_attributes = {'service_name': self.config['service_name']}

    self.service_name = self.config['service_name']

  def dumpConfig(self):
    logger.info(self.__dict__)
