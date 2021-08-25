"""
Agent configuration logic that pull in values from a defaults list,
environment variables, and the agent-config.yaml file.
"""
import json
import os
import logging
import traceback
import yaml
from google.protobuf import json_format as jf
from google.protobuf.wrappers_pb2 import BoolValue
from hypertrace.agent.config import config_pb2
from hypertrace.agent.config.default import *
from .file import load_config_from_file
from .environment import load_config_from_env

# Configuration attributes specific to pythonagent
PYTHON_SPECIFIC_ATTRIBUTES: list = [
    '_use_console_span_exporter'
]

# Initialize logger
logger = logging.getLogger(__name__)  # pylint: disable=C0103


def merge_config(base_config, overriding_config):
    """
    Returns the merged result of two configs recursively
    """

    for key in overriding_config:
        if key in base_config and isinstance(base_config[key], dict):
            if key in overriding_config:
                base_config[key] = merge_config(
                    base_config[key], overriding_config[key])
        else:
            if key == 'propagation_formats':
                logger.debug('Merging propagation_formats values.')
                if hasattr(base_config, key):
                    base_config[key] = set(
                        base_config[key].extend(overriding_config[key]))
                else:
                    base_config[key] = overriding_config[key]
            else:
                base_config[key] = overriding_config[key]
    return base_config

# Read agent-config file and override with environment variables as necessaary


class AgentConfig:  # pylint: disable=R0902,R0903
    '''A wrapper around the agent configuration logic'''

    def __init__(self):  # pylint: disable=R0912,R0915
        """
        Returns a new instance of config_pb2.AgentConfig when a new AgentConfig() is created.
        If 'HT_CONFIG_FILE' is specified in the environment data would be loaded from that file.
        If not, data would be loaded from 'DEFAULT_AGENT_CONFIG' on 'default.py'
        """

        config_dict = DEFAULT_AGENT_CONFIG
        custom_config = {}
        file_dict = _read_from_file()
        if file_dict is not None:
            config_dict = merge_config(config_dict, file_dict)
            custom_config = merge_config(custom_config, file_dict)

        env_dict = load_config_from_env()
        config_dict = merge_config(config_dict, env_dict)
        custom_config = merge_config(custom_config, env_dict)

        config = config_pb2.AgentConfig()
        json_string = json.dumps(config_dict)
        jf.Parse(json_string, config)

        logger.debug("Successfully loaded config %s", str(config_dict))

        self.config = config
        self.agent_config = config
        self.custom_config = custom_config

        # # Create Protobuf AgentConfig object
        # #
        # # Create Protobuf Opa object
        # opa = jf.Parse(jf.MessageToJson(config_pb2.Opa()), config_pb2.Opa)
        # opa.endpoint = self.config['reporting']['opa']['endpoint']
        # opa.poll_period_seconds = self.config['reporting']['opa']['poll_period_seconds']
        # opa.enabled = self.config['reporting']['opa']['enabled']
        #
        # # Create protobuf Reporting object
        # reporting = jf.Parse(jf.MessageToJson(
        #     config_pb2.Reporting()), config_pb2.Reporting)
        # reporting.endpoint = self.config['reporting']['endpoint']
        # reporting.secure = self.config['reporting']['secure']
        # reporting.token = self.config['reporting']['token']
        # reporting.opa = opa
        #
        # # Set trace_reporter_type
        # if self.config['reporting']['trace_reporter_type'] == 'OTLP':
        #     reporting.trace_reporter_type = config_pb2.TraceReporterType.OTLP
        # elif self.config['reporting']['trace_reporter_type'] == 'ZIPKIN':
        #     reporting.trace_reporter_type = config_pb2.TraceReporterType.ZIPKIN
        # else:
        #     # Default to ZIPKIN
        #     reporting.trace_reporter_type = config_pb2.TraceReporterType.OTLP
        #
        # # Create DataCapture Message components
        # rpc_body = config_pb2.Message(request=BoolValue(
        #     value=self.config['data_capture']['rpc_body']['request']),
        #     response=BoolValue(
        #         value=self.config['data_capture']['rpc_body']['response']))
        # rpc_metadata = config_pb2.Message(request=BoolValue(
        #     value=self.config['data_capture']['rpc_metadata']['request']),
        #     response=BoolValue(
        #         value=self.config['data_capture']['rpc_metadata']['response']))
        # http_body = config_pb2.Message(request=BoolValue(
        #     value=self.config['data_capture']['http_body']['request']),
        #     response=BoolValue(
        #         value=self.config['data_capture']['http_body']['response']))
        # http_headers = config_pb2.Message(request=BoolValue(
        #     value=self.config['data_capture']['http_headers']['request']),
        #     response=BoolValue(
        #         value=self.config['data_capture']['http_headers']['response']))
        #
        # # Create Protobuf DataCapture object
        # data_capture = jf.Parse(jf.MessageToJson(
        #     config_pb2.DataCapture()), config_pb2.DataCapture)
        # data_capture.http_headers = http_headers
        # data_capture.http_body = http_body
        # data_capture.rpc_metadata = rpc_metadata
        # data_capture.rpc_body = rpc_body
        # data_capture.body_max_size_bytes = self.config['data_capture']['body_max_size_bytes']
        #
        # # Create Protobuf AgentConfig object
        # self.agent_config: config_pb2.AgentConfig = jf.Parse(jf.MessageToJson(
        #     config_pb2.AgentConfig()), config_pb2.AgentConfig)
        # self.agent_config.service_name = self.config['service_name']
        # self.agent_config.reporting = reporting
        # self.agent_config.data_capture = data_capture
        # tmp_propagation_formats = []
        # if 'TRACECONTEXT' in self.config['propagation_formats']:
        #     tmp_propagation_formats.append(
        #         config_pb2.PropagationFormat.TRACECONTEXT)
        #     tmp_propagation_formats = list(set(tmp_propagation_formats))
        # if 'B3' in self.config['propagation_formats']:
        #     tmp_propagation_formats.append(config_pb2.PropagationFormat.B3)
        #     tmp_propagation_formats = list(set(tmp_propagation_formats))
        # if not tmp_propagation_formats:
        #     # Default to TRACECONTEXT
        #     tmp_propagation_formats.append(
        #         config_pb2.PropagationFormat.TRACECONTEXT)
        # self.agent_config.propagation_formats = tmp_propagation_formats
        # self.agent_config.enabled = self.config['enabled']
        #
        # self.agent_config.resource_attributes = self.config['resource_attributes']

    def dump_config(self):
        '''Dump configuration information.'''
        logger.debug(self.__dict__)

    def use_console_span_exporter(self) -> bool:
        '''Initialize InMemorySpanExporter'''
        return self.custom_config.get('_use_console_span_exporter')


def _apply_custom_config_options(current_custom, next_config):
    for key in PYTHON_SPECIFIC_ATTRIBUTES:
        if next_config[key]:
            current_custom[key] = next_config[key]
    return current_custom


def _read_from_file():
    if 'HT_CONFIG_FILE' in os.environ:
        if len(os.environ['HT_CONFIG_FILE']) == 0:
            # HT_CONFIG_FILE can be passed as empty string which is invalid
            logger.error(
                'Failed to load HT_CONFIG_FILE env var is empty')
            return None
        else:
            config_from_file = load_config_from_file(os.environ['HT_CONFIG_FILE'])

            logger.debug('Successfully loaded config file')
            return config_from_file
    return None
