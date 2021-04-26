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
logger = logging.getLogger(__name__)

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
            path = os.path.abspath(os.environ['HT_CONFIG_FILE'])
            file = open(path, 'r')
            from_file_config = yaml.load(file, Loader=yaml.FullLoader)
            file.close()
            logger.debug("Loading config from %s", path)
            self.config = merge_config(DEFAULT_AGENT_CONFIG, from_file_config)
        else:
            self.config = DEFAULT_AGENT_CONFIG

        # Use variables from environment:
        if 'HT_SERVICE_NAME' in os.environ:
            logger.debug("[env] Loaded HT_SERVICE_NAME from env")
            # set local variable
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
            self.config['reporting_token'] = os.environ['HT_REPORTING_TOKEN']

        if 'HT_REPORTING_OPA_ENDPOINT' in os.environ:
            logger.debug("[env] Loaded HT_REPORTING_OPA_ENDPOINT from env")
            self.config['opa_endpoint'] = os.environ['HT_REPORTING_OPA_ENDPOINT']


        if 'HT_REPORTING_OPA_POLL_PERIOD_SECONDS' in os.environ:
            logger.debug(
                "[env] Loaded HT_REPORTING_OPA_POLL_PERIOD_SECONDS from env")
            self.config['opa_poll_period_seconds'] = os.environ['HT_REPORTING_OPA_POLL_PERIOD_SECONDS']

        if 'HT_REPORTING_OPA_ENABLED' in os.environ:
            logger.debug("[env] Loaded HT_REPORTING_OPA_ENABLED from env")
            self.config['opa_enabled'] = os.environ['HT_REPORTING_OPA_ENABLED'].lower(
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
            self.config['data_capture_max_size_bytes'] \
                = int(os.environ['HT_DATA_CAPTURE_BODY_MAX_SIZE_BYTES'])

        if 'HT_PROPAGATION_FORMATS' in os.environ:
            logger.debug("[env] Loaded HT_PROPAGATION_FORMATS from env")
            self.config['propagation_formats'] = os.environ['HT_PROPAGATION_FORMATS']

        if 'HT_ENABLED' in os.environ:
            logger.debug("[env] Loaded HT_ENABLED from env")
            self.config['hypertrace_enabled'] = os.environ['HT_ENABLED'].lower() == 'true'

        if 'HT_ENABLE_CONSOLE_SPAN_EXPORTER' in os.environ:
            logger.debug("[env] Loaded HT_ENABLE_CONSOLE_SPAN_EXPORTER from env, %s",
                         str(os.environ['HT_ENABLE_CONSOLE_SPAN_EXPORTER'].lower()))
            self.config['_use_console_span_exporter'] = \
              os.environ['HT_ENABLE_CONSOLE_SPAN_EXPORTER'].lower() == 'true'

        self.opa = jf.Parse(jf.MessageToJson(config_pb2.Opa()), config_pb2.Opa)
        # self.opa.endpoint = opa_endpoint
        # self.opa.poll_period_seconds = opa_poll_period_seconds
        # self.opa.enabled = opa_enabled

        self.reporting = jf.Parse(jf.MessageToJson(
            config_pb2.Reporting()), config_pb2.Reporting)
        # 'https://localhost'
        self.reporting.endpoint = self.config['reporting']['endpoint']
        self.reporting.secure = self.config['reporting']['secure']
        self.reporting.token = self.config['reporting_token']
        self.reporting.opa = self.config['opa_enabled']

        if "trace_reporter_type" in self.config['reporting'] and \
                self.config['reporting']['trace_reporter_type']:
            self.reporting.trace_reporter_type = self.config['reporting']['trace_reporter_type']
        else:
            self.reporting.trace_reporter_type = config_pb2.TraceReporterType.OTLP
        self.rpc_body = config_pb2.Message(request=BoolValue(
            value=self.config['data_capture']['rpc_body']['request']),
            response=BoolValue(
                value=self.config['data_capture']['rpc_body']['response']))
        self.rpc_metadata = config_pb2.Message(request=BoolValue(
            value=self.config['data_capture']['rpc_metadata']['request']),
            response=BoolValue(
                value=self.config['data_capture']['rpc_metadata']['response']))
        self.http_body = config_pb2.Message(request=BoolValue(
            value=self.config['data_capture']['http_body']['request']),
            response=BoolValue(
                value=self.config['data_capture']['http_body']['response']))
        self.http_headers = config_pb2.Message(request=BoolValue(
            value=self.config['data_capture']['http_headers']['request']),
            response=BoolValue(
                value=self.config['data_capture']['http_headers']['response']))

        self.data_capture = jf.Parse(jf.MessageToJson(
            config_pb2.DataCapture()), config_pb2.DataCapture)
        self.data_capture.http_headers = self.http_headers
        self.data_capture.http_body = self.http_body
        self.data_capture.rpc_metadata = self.rpc_metadata
        self.data_capture.rpc_body = self.rpc_body
        self.data_capture.body_max_size_bytes = self.config['data_capture_max_size_bytes']

        self.agent_config: config_pb2.AgentConfig = jf.Parse(jf.MessageToJson(
            config_pb2.AgentConfig()), config_pb2.AgentConfig)
        self.agent_config.service_name = self.config['service_name']
        self.agent_config.reporting = self.reporting
        self.agent_config.data_capture = self.data_capture
        if self.config['propagation_formats']  == 'TRACECONTEXT':
            self.agent_config.propagation_formats = config_pb2.PropagationFormat.TRACECONTEXT
        else:
            self.agent_config.propagation_formats = config_pb2.PropagationFormat.B3
        self.agent_config.enabled = self.config['agent_config_enabled']

        self.agent_config.resource_attributes = {
            'service_name': self.config['service_name']}

        self.service_name = self.config['service_name']



    def dump_config(self):
        '''Dump configuration information.'''
        logger.debug(self.__dict__)

    def get_config(self):
        '''Return configuration information.'''
        return self.agent_config

    def use_console_span_exporter(self) -> bool:
        '''Initialize InMemorySpanExporter'''
        self.config['_use_console_span_exporter']