"""
Agent configuration logic that pull in values from a defaults list,
environment variables, and the agent-config.yaml file.
"""
import os
import logging
import yaml
from google.protobuf import json_format as jf
from google.protobuf.wrappers_pb2 import BoolValue
from hypertrace.agent.config import config_pb2
from hypertrace.agent.config.default import *

# Initialize logger
logger = logging.getLogger(__name__)  # pylint: disable=C0103

def merge_config(base_config, overriding_config):
    """
    Returns the merged result of two configs recursively
    """

    for key in overriding_config:
        if key in base_config and isinstance(base_config[key], dict):
            base_config[key] = merge_config(
                base_config[key], overriding_config[key])
        else:
            base_config[key] = overriding_config[key]
    return base_config


# Read agent-config file and override with environment variables as necessaary

class AgentConfig1:  # pylint: disable=R0902,R0903
    '''A wrapper around the agent configuration logic'''

    def __init__(self):  # pylint: disable=R0912,R0915
        """
        Returns a new instance of config_pb2.AgentConfig when a new AgentConfig() is created.
        If 'HT_CONFIG_FILE' is specified in the environment data would be loaded from that file.
        If not, data would be loaded from 'DEFAULT_AGENT_CONFIG' on 'default.py'
        """

        self.config = None
        if 'HT_CONFIG_FILE' in os.environ:
            path = os.path.abspath(os.environ['HT_CONFIG_FILE'])
            file = open(path, 'r')
            from_file_config = yaml.load(file, Loader=yaml.FullLoader)
            file.close()

            logger.debug("Loading config from %s", path)
            self.config = merge_config(DEFAULT_AGENT_CONFIG, from_file_config)
        else:
            self.config = DEFAULT_AGENT_CONFIG

        reporting_token = ""
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
            self.config['reporting']['secure'] = os.environ['HT_REPORTING_SECURE'].lower(
            ) == 'true'

        if 'HT_REPORTING_TOKEN' in os.environ:
            logger.debug("[env] Loaded HT_REPORTING_TOKEN from env")
            reporting_token = os.environ['HT_REPORTING_TOKEN']

        if 'HT_REPORTING_OPA_ENDPOINT' in os.environ:
            logger.debug("[env] Loaded HT_REPORTING_OPA_ENDPOINT from env")
            opa_endpoint = os.environ['HT_REPORTING_OPA_ENDPOINT']

        if 'HT_REPORTING_OPA_POLL_PERIOD_SECONDS' in os.environ:
            logger.debug(
                "[env] Loaded HT_REPORTING_OPA_POLL_PERIOD_SECONDS from env")
            opa_poll_period_seconds = os.environ['HT_REPORTING_OPA_POLL_PERIOD_SECONDS']

        if 'HT_REPORTING_OPA_ENABLED' in os.environ:
            logger.debug("[env] Loaded HT_REPORTING_OPA_ENABLED from env")
            opa_enabled = os.environ['HT_REPORTING_OPA_ENABLED'].lower(
            ) == 'true'

        if 'HT_DATA_CAPTURE_HTTP_HEADERS_REQUEST' in os.environ:
            logger.debug(
                "[env] Loaded HT_DATA_CAPTURE_HTTP_HEADERS_REQUEST from env")
            self.config['data_capture']['http_headers']['request'] \
                = os.environ['HT_DATA_CAPTURE_HTTP_HEADERS_REQUEST'].lower() \
                  == 'true'

        if 'HT_DATA_CAPTURE_HTTP_HEADERS_RESPONSE' in os.environ:
            logger.debug(
                "[env] Loaded HT_DATA_CAPTURE_HTTP_HEADERS_RESPONSE from env")
            self.config['data_capture']['http_headers']['response'] \
                = os.environ['HT_DATA_CAPTURE_HTTP_HEADERS_RESPONSE'].lower() \
                  == 'true'

        if 'HT_DATA_CAPTURE_HTTP_BODY_REQUEST' in os.environ:
            logger.debug(
                "[env] Loaded HT_DATA_CAPTURE_HTTP_BODY_REQUEST from env")
            self.config['data_capture']['http_body']['request'] \
                = os.environ['HT_DATA_CAPTURE_HTTP_BODY_REQUEST'].lower() \
                  == 'true'

        if 'HT_DATA_CAPTURE_HTTP_BODY_RESPONSE' in os.environ:
            logger.debug(
                "[env] Loaded HT_DATA_CAPTURE_HTTP_BODY_RESPONSE from env")
            self.config['data_capture']['http_body']['response'] \
                = os.environ['HT_DATA_CAPTURE_HTTP_BODY_RESPONSE'].lower() \
                  == 'true'

        if 'HT_DATA_CAPTURE_RPC_METADATA_REQUEST' in os.environ:
            logger.debug(
                "[env] Loaded HT_DATA_CAPTURE_RPC_METADATA_REQUEST from env")
            self.config['data_capture']['rpc_metadata']['request'] \
                = os.environ['HT_DATA_CAPTURE_RPC_METADATA_REQUEST'].lower() \
                  == 'true'

        if 'HT_DATA_CAPTURE_RPC_METADATA_RESPONSE' in os.environ:
            logger.debug(
                "[env] Loaded HT_DATA_CAPTURE_RPC_METADATA_RESPONSE from env")
            self.config['data_capture']['rpc_metadata']['response'] \
                = os.environ['HT_DATA_CAPTURE_RPC_METADATA_RESPONSE'].lower() \
                  == 'true'

        if 'HT_DATA_CAPTURE_RPC_BODY_REQUEST' in os.environ:
            logger.debug(
                "[env] Loaded HT_DATA_CAPTURE_RPC_BODY_REQUEST from env")
            self.config['data_capture']['rpc_body']['request'] \
                = os.environ['HT_DATA_CAPTURE_RPC_BODY_REQUEST'].lower() \
                  == 'true'

        if 'HT_DATA_CAPTURE_RPC_BODY_RESPONSE' in os.environ:
            logger.debug(
                "[env] Loaded HT_DATA_CAPTURE_RPC_BODY_RESPONSE from env")
            self.config['data_capture']['rpc_body']['response'] \
                = os.environ['HT_DATA_CAPTURE_RPC_BODY_RESPONSE'].lower() \
                  == 'true'

        if 'HT_DATA_CAPTURE_BODY_MAX_SIZE_BYTES' in os.environ:
            logger.debug(
                "[env] Loaded HT_DATA_CAPTURE_BODY_MAX_SIZE_BYTES from env")
            data_capture_max_size_bytes \
                = int(os.environ['HT_DATA_CAPTURE_BODY_MAX_SIZE_BYTES'])

        if 'HT_PROPAGATION_FORMATS' in os.environ:
            logger.debug("[env] Loaded HT_PROPAGATION_FORMATS from env")
            self.propagation_formats = os.environ['HT_PROPAGATION_FORMATS']
        else:
            self.propagation_formats = DEFAULT_PROPAGATION_FORMAT

        if 'HT_ENABLED' in os.environ:
            logger.debug("[env] Loaded HT_ENABLED from env")
            agent_config_enabled = os.environ['HT_ENABLED'].lower() == 'true'

        self.opa = jf.Parse(jf.MessageToJson(config_pb2.Opa()), config_pb2.Opa)
        self.opa.endpoint = opa_endpoint
        self.opa.poll_period_seconds = opa_poll_period_seconds
        self.opa.enabled = opa_enabled

        self.reporting = jf.Parse(jf.MessageToJson(
            config_pb2.Reporting()), config_pb2.Reporting)
        # 'https://localhost'
        self.reporting.endpoint = self.config['reporting']['endpoint']
        self.reporting.secure = self.config['reporting']['secure']
        self.reporting.token = reporting_token
        self.reporting.opa = self.opa

        if "trace_reporter_type" in self.config['reporting'] and \
                self.config['reporting']['trace_reporter_type']:
            self.reporting.trace_reporter_type = self.config['reporting']['trace_reporter_type']
        else:
            self.reporting.trace_reporter_type = config_pb2.TraceReporterType.OTLP
        self.rpc_body = config_pb2.Message(request=BoolValue(  # pylint: disable=C0330
            value=self.config['data_capture']['rpc_body']['request']),
            response=BoolValue(  # pylint: disable=C0330
                value=self.config['data_capture']['rpc_body']['response']))  # pylint: disable=C0330
        self.rpc_metadata = config_pb2.Message(request=BoolValue(  # pylint: disable=C0330
            value=self.config['data_capture']['rpc_metadata']['request']),
            response=BoolValue(  # pylint: disable=C0330
                value=self.config['data_capture']['rpc_metadata']['response']))  # pylint: disable=C0330
        self.http_body = config_pb2.Message(request=BoolValue(  # pylint: disable=C0330
            value=self.config['data_capture']['http_body']['request']),
            response=BoolValue(  # pylint: disable=C0330
                value=self.config['data_capture']['http_body']['response']))  # pylint: disable=C0330
        self.http_headers = config_pb2.Message(request=BoolValue(  # pylint: disable=C0330
            value=self.config['data_capture']['http_headers']['request']),
            response=BoolValue(  # pylint: disable=C0330
                value=self.config['data_capture']['http_headers']['response']))  # pylint: disable=C0330

        self.data_capture = jf.Parse(jf.MessageToJson(
            config_pb2.DataCapture()), config_pb2.DataCapture)
        self.data_capture.http_headers = self.http_headers
        self.data_capture.http_body = self.http_body
        self.data_capture.rpc_metadata = self.rpc_metadata
        self.data_capture.rpc_body = self.rpc_body
        self.data_capture.body_max_size_bytes = data_capture_max_size_bytes

        self.agent_config: config_pb2.AgentConfig = jf.Parse(jf.MessageToJson(
            config_pb2.AgentConfig()), config_pb2.AgentConfig)
        self.agent_config.service_name = self.config['service_name']
        self.agent_config.reporting = self.reporting
        self.agent_config.data_capture = self.data_capture
        if self.propagation_formats == 'TRACECONTEXT':
            self.agent_config.propagation_formats = config_pb2.PropagationFormat.TRACECONTEXT
        else:
            self.agent_config.propagation_formats = config_pb2.PropagationFormat.B3
        self.agent_config.enabled = agent_config_enabled
        self.agent_config.resource_attributes = {
            'service_name': self.config['service_name']}

        self.service_name = self.config['service_name']

    def parse_config1(self, parent_key):
        '''configuration parsing helper'''
        for sub_key in DEFAULT_AGENT_CONFIG[parent_key].keys():
            if sub_key in self.new_config[parent_key] \
                    and isinstance(DEFAULT_AGENT_CONFIG[parent_key][sub_key], dict):
                for value_key in DEFAULT_AGENT_CONFIG[parent_key][sub_key].keys():
                    if value_key in self.new_config[parent_key][sub_key]:
                        value = self.new_config[parent_key][sub_key][value_key]
                        self.config[parent_key][sub_key][value_key] = value
                        logger.debug(
                            "[YAML] %s.%s.%s -> %s", parent_key, sub_key, value_key, value)
                    else:
                        value = DEFAULT_AGENT_CONFIG[parent_key][sub_key][value_key]
                        self.config[parent_key][sub_key][value_key] = value
                        logger.debug(
                            "[DEFAULT] %s.%s.%s -> %s", parent_key, sub_key, value_key, value)
            else:
                value = DEFAULT_AGENT_CONFIG[parent_key][sub_key]
                self.config[parent_key][sub_key] = value
                logger.debug(
                    "[DEFAULT] %s.%s -> %s", parent_key, sub_key, value)

    def dump_config(self):
        '''Dump configuration information.'''
        logger.debug(self.__dict__)

    def get_config1(self) -> config_pb2.AgentConfig:
        '''Return configuration information.'''
        return self.agent_config
