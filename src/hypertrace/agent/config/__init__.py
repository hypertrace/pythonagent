"""
Agent configuration logic that pull in values from a defaults list,
environment variables, and the agent-config.yaml file.
"""
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

        self.config = None
        if 'HT_CONFIG_FILE' in os.environ:
            if len(os.environ['HT_CONFIG_FILE']) == 0:
                # HT_CONFIG_FILE can be passed as empty string which is invalid
                logger.error(
                    'Failed to load HT_CONFIG_FILE env var being empty')
            else:
                config_from_file = load_config_from_file(
                    os.environ['HT_CONFIG_FILE'])

                self.config = merge_config(
                    DEFAULT_AGENT_CONFIG, config_from_file)

                logger.debug(
                    'Successfully loaded config, config=%s', str(self.config))
        else:
            logger.info('Loading default configuration.')
            self.config = DEFAULT_AGENT_CONFIG

        self.config = merge_config(self.config, load_config_from_env())

        # Create Protobuf AgentConfig object
        #
        # Create Protobuf Opa object
        opa = jf.Parse(jf.MessageToJson(config_pb2.Opa()), config_pb2.Opa)
        opa.endpoint = self.config['reporting']['opa']['endpoint']
        opa.poll_period_seconds = self.config['reporting']['opa']['poll_period_seconds']
        opa.enabled = self.config['reporting']['opa']['enabled']

        # Create protobuf Reporting object
        reporting = jf.Parse(jf.MessageToJson(
            config_pb2.Reporting()), config_pb2.Reporting)
        reporting.endpoint = self.config['reporting']['endpoint']
        reporting.secure = self.config['reporting']['secure']
        reporting.token = self.config['reporting']['token']
        reporting.opa = opa

        # Set trace_reporter_type
        if self.config['reporting']['trace_reporter_type'] == 'OTLP':
            reporting.trace_reporter_type = config_pb2.TraceReporterType.OTLP
        elif self.config['reporting']['trace_reporter_type'] == 'ZIPKIN':
            reporting.trace_reporter_type = config_pb2.TraceReporterType.ZIPKIN
        else:
            # Default to ZIPKIN
            reporting.trace_reporter_type = config_pb2.TraceReporterType.OTLP

        # Create DataCapture Message components
        rpc_body = config_pb2.Message(request=BoolValue(
            value=self.config['data_capture']['rpc_body']['request']),
            response=BoolValue(
                value=self.config['data_capture']['rpc_body']['response']))
        rpc_metadata = config_pb2.Message(request=BoolValue(
            value=self.config['data_capture']['rpc_metadata']['request']),
            response=BoolValue(
                value=self.config['data_capture']['rpc_metadata']['response']))
        http_body = config_pb2.Message(request=BoolValue(
            value=self.config['data_capture']['http_body']['request']),
            response=BoolValue(
                value=self.config['data_capture']['http_body']['response']))
        http_headers = config_pb2.Message(request=BoolValue(
            value=self.config['data_capture']['http_headers']['request']),
            response=BoolValue(
                value=self.config['data_capture']['http_headers']['response']))

        # Create Protobuf DataCapture object
        data_capture = jf.Parse(jf.MessageToJson(
            config_pb2.DataCapture()), config_pb2.DataCapture)
        data_capture.http_headers = http_headers
        data_capture.http_body = http_body
        data_capture.rpc_metadata = rpc_metadata
        data_capture.rpc_body = rpc_body
        data_capture.body_max_size_bytes = self.config['data_capture']['body_max_size_bytes']

        # Create Protobuf AgentConfig object
        self.agent_config: config_pb2.AgentConfig = jf.Parse(jf.MessageToJson(
            config_pb2.AgentConfig()), config_pb2.AgentConfig)
        self.agent_config.service_name = self.config['service_name']
        self.agent_config.reporting = reporting
        self.agent_config.data_capture = data_capture
        tmp_propagation_formats = []
        if 'TRACECONTEXT' in self.config['propagation_formats']:
            tmp_propagation_formats.append(
                config_pb2.PropagationFormat.TRACECONTEXT)
            tmp_propagation_formats = list(set(tmp_propagation_formats))
        if 'B3' in self.config['propagation_formats']:
            tmp_propagation_formats.append(config_pb2.PropagationFormat.B3)
            tmp_propagation_formats = list(set(tmp_propagation_formats))
        if not tmp_propagation_formats:
            # Default to TRACECONTEXT
            tmp_propagation_formats.append(
                config_pb2.PropagationFormat.TRACECONTEXT)
        self.agent_config.propagation_formats = tmp_propagation_formats
        self.agent_config.enabled = self.config['enabled']

        self.agent_config.resource_attributes = self.config['resource_attributes']

        # Validate configuration
        self.validate_config_elements(self.config, self.agent_config)

    def validate_config_elements(self, config_element, agent_config_base):
        """Validate that all present elements in the parse configuration are
        defined in the config_pb2.AgentConfig"""
        # Check for configuration entries that do not belong
        for key in config_element:
            logger.debug('Checking key=%s, type=%s', key,
                         str(type(config_element[key])))
            if isinstance(config_element[key], dict):
                try:
                    if not hasattr(agent_config_base, key):
                        logger.error(
                            'Unknown attribute encountered. key=%s', key)
                    logger.debug('config_element=%s, agent_config_base=%s',
                                 str(config_element),
                                 str(agent_config_base))
                    if key == 'resource_attributes':
                        continue
                    self.validate_config_elements(config_element[key],
                                                  getattr(agent_config_base, key))  # pylint: disable=W0123
                    continue
                except AttributeError as err:
                    logger.error('Unknown attribute encountered: exception=%s, stacktrace=%s',
                                 err,
                                 traceback.format_exc())
                    continue
            elif isinstance(config_element[key], (str, bool, int, list)):
                if key in PYTHON_SPECIFIC_ATTRIBUTES:
                    logger.debug(
                        'Found pythonagent-specific attribute, attr=%s', key)
                    continue
                try:
                    if hasattr(agent_config_base, key):
                        #                      and key != 'propagation_formats':
                        logger.debug('Is valid: %s', key)
                    else:
                        logger.debug('Not valid: %s', key)
                        raise AttributeError
                except AttributeError as err:
                    logger.error('Unknown attribute %s encountered: exception=%s, stacktrace=%s',
                                 key,
                                 err,
                                 traceback.format_exc())
            else:
                logger.error('Unknown attribute type encountered: exception=%s, stacktrace=%s',
                             err,
                             traceback.format_exc())

    def dump_config(self):
        '''Dump configuration information.'''
        logger.debug(self.__dict__)

    def get_config(self) -> config_pb2.AgentConfig:
        '''Return configuration information.'''
        return self.agent_config

    def use_console_span_exporter(self) -> bool:
        '''Initialize InMemorySpanExporter'''
        return self.config['_use_console_span_exporter']
