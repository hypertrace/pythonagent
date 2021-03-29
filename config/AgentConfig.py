import os

import yaml
from google.protobuf import json_format as jf
from google.protobuf.wrappers_pb2 import BoolValue

from config import config_pb2 as config_pb2
from config.AgentConfig_default import *
from config.logger import get_logger

logger = get_logger(__name__)


class AgentConfig:
    def __new__(cls, *args, **kwargs):
        """
        Returns a new instance of config_pb2.AgentConfig when a new AgentConfig() is created.
        If 'AGENT_YAML' is specified in the environment data would be loaded from that file.
        If not, data would be loaded from 'DEFAULT_AGENT_CONFIG' on 'AgentConfig_default.py'
        """

        config = DEFAULT_AGENT_CONFIG
        new_config = None
        if 'AGENT_YAML' in os.environ:
            path = os.path.abspath(os.environ['AGENT_YAML'])
            logger.debug("AgentConfig - using file from %s", path)

            file = open(path, 'r')
            new_config = yaml.load(file, Loader=yaml.FullLoader)
            file.close()
        else:
            logger.debug("AgentConfig - using default")

        opa = jf.Parse(jf.MessageToJson(config_pb2.Opa()), config_pb2.Opa)
        opa.endpoint = DEFAULT_OPA_ENDPOINT,
        opa.poll_period_seconds = DEFAULT_OPA_POLL_PERIOD_SECONDS,
        opa.enabled = DEFAULT_OPA_ENABLED

        reporting = jf.Parse(jf.MessageToJson(config_pb2.Reporting()), config_pb2.Reporting)
        reporting.endpoint = config['reporting']['endpoint']  # 'https://localhost'
        reporting.secure = config['reporting']['secure']
        reporting.token = DEFAULT_REPORTING_TOKEN
        reporting.opa = opa
        reporting.trace_reporter_type = config_pb2.TraceReporterType.OTLP

        if new_config:
            for parentKey in DEFAULT_AGENT_CONFIG.keys():
                if parentKey in new_config:
                    if type(DEFAULT_AGENT_CONFIG[parentKey]) is dict:
                        for subKey in DEFAULT_AGENT_CONFIG[parentKey].keys():
                            if subKey in new_config[parentKey]:
                                if type(DEFAULT_AGENT_CONFIG[parentKey][subKey]) is dict:
                                    for valueKey in DEFAULT_AGENT_CONFIG[parentKey][subKey].keys():
                                        if valueKey in new_config[parentKey][subKey]:
                                            value = new_config[parentKey][subKey][valueKey]
                                            logger.debug("[YAML] %s.%s.%s -> %s", parentKey, subKey, valueKey, value)
                                        else:
                                            value = DEFAULT_AGENT_CONFIG[parentKey][subKey][valueKey]
                                            config[parentKey][subKey][valueKey] = value
                                            logger.debug("[DEFAULT] %s.%s.%s -> %s", parentKey, subKey, valueKey, value)
                                else:
                                    value = DEFAULT_AGENT_CONFIG[parentKey][subKey]
                                    logger.debug("[YAML] %s.%s -> %s", parentKey, subKey, value)
                            else:
                                value = DEFAULT_AGENT_CONFIG[parentKey][subKey]
                                config[parentKey][subKey] = value
                                logger.debug("[DEFAULT] %s.%s -> %s", parentKey, subKey, value)
                    else:
                        logger.debug("[YAML] %s -> %s", parentKey, config[parentKey])
                else:
                    value = DEFAULT_AGENT_CONFIG[parentKey]
                    config[parentKey] = value
                    logger.debug("[DEFAULT] %s -> %s", parentKey, value)

        rpc_body = config_pb2.Message(request=BoolValue(value=config['data_capture']['rpc_body']['request']),
                                      response=BoolValue(value=config['data_capture']['rpc_body']['response']))
        rpc_metadata = config_pb2.Message(request=BoolValue(value=config['data_capture']['rpc_metadata']['request']),
                                          response=BoolValue(value=config['data_capture']['rpc_metadata']['response']))
        http_body = config_pb2.Message(request=BoolValue(value=config['data_capture']['http_body']['request']),
                                       response=BoolValue(value=config['data_capture']['http_body']['response']))
        http_headers = config_pb2.Message(request=BoolValue(value=config['data_capture']['http_headers']['request']),
                                          response=BoolValue(value=config['data_capture']['http_headers']['response']))

        data_capture = jf.Parse(jf.MessageToJson(config_pb2.DataCapture()), config_pb2.DataCapture)
        data_capture.http_headers = http_headers
        data_capture.http_body = http_body
        data_capture.rpc_metadata = rpc_metadata
        data_capture.rpc_body = rpc_body
        data_capture.body_max_size_bytes = DEFAULT_DATA_CAPTURE_MAX_SIZE_BYTES

        java_agent = jf.Parse(jf.MessageToJson(config_pb2.JavaAgent()), config_pb2.JavaAgent)
        java_agent.filter_jar_paths = DEFAULT_JAVA_AGENT_PATH  # not needed for python

        agent_config = jf.Parse(jf.MessageToJson(config_pb2.AgentConfig()), config_pb2.AgentConfig)
        agent_config.service_name = config['service_name']
        agent_config.reporting = reporting
        agent_config.data_capture = data_capture
        agent_config.propagation_formats = config_pb2.PropagationFormat.TRACECONTEXT
        agent_config.enabled = DEFAULT_AGENT_CONFIG_ENABLED
        agent_config.javaagent = java_agent
        agent_config.resource_attributes = {'service_name': config['service_name']}

        return agent_config
