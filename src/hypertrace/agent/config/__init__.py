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
                logger.debug('base_config[key]=%s', str(base_config[key]))
                if hasattr(base_config, key):
                    base_config[key] = set(base_config[key].extend(overriding_config[key]))
                else:
                    base_config[key] = overriding_config[key]
            else:
                base_config[key] = overriding_config[key]
    return base_config


def load_config_from_file(filepath):
    """
    Returns the config loaded from a provided config file
    """
    logger.debug(
        'HT_CONFIG_FILE is set %s. Attempting to load the config file', filepath)
    try:
        path = os.path.abspath(filepath)

        file = open(path, 'r')
        from_file_config = yaml.load(file, Loader=yaml.FullLoader)
        file.close()

        logger.debug('Successfully load config from %s', path)

        return from_file_config
    except Exception as err:  # pylint: disable=W0703
        logger.error('Failed to load HT_CONFIG_FILE: exception=%s, stacktrace=%s',
                     err,
                     traceback.format_exc())
        logger.info('Loading default configuration.')
        return DEFAULT_AGENT_CONFIG

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

        if "reporting" not in self.config:
            self.config['reporting'] = {}
            self.config['reporting']['opa'] = {}
        # Use variables from environment:
        if 'HT_SERVICE_NAME' in os.environ:
            logger.debug("[env] Loaded HT_SERVICE_NAME from env")
            # set local variable
            self.config['service_name'] = os.environ['HT_SERVICE_NAME']

        if 'HT_REPORTING_ENDPOINT' in os.environ:
            logger.debug("[env] Loaded HT_REPORTING_ENDPOINT from env")
            self.config['reporting']['endpoint'] = os.environ['HT_REPORTING_ENDPOINT']

        if 'HT_TRACES_EXPORTER' in os.environ:
            logger.debug("[env] Loaded HT_TRACES_EXPORTER from env")
            self.config['reporting']['trace_reporter_type'] = os.environ['HT_TRACES_EXPORTER']

        if 'HT_REPORTING_SECURE' in os.environ:
            logger.debug("[env] Loaded HT_REPORTING_SECURE from env")
            self.config['reporting']['secure'] = os.environ['HT_REPORTING_SECURE'].lower(
            ) == 'true'

        if 'HT_REPORTING_TOKEN' in os.environ:
            logger.debug("[env] Loaded HT_REPORTING_TOKEN from env")
            self.config['reporting']['token'] = os.environ['HT_REPORTING_TOKEN']

        if 'HT_REPORTING_OPA_ENDPOINT' in os.environ:
            logger.debug("[env] Loaded HT_REPORTING_OPA_ENDPOINT from env")
            self.config['reporting']['opa']['endpoint'] = os.environ['HT_REPORTING_OPA_ENDPOINT']

        if 'HT_REPORTING_OPA_POLL_PERIOD_SECONDS' in os.environ:
            logger.debug(
                "[env] Loaded HT_REPORTING_OPA_POLL_PERIOD_SECONDS from env")
            self.config['reporting']['opa']['poll_period_seconds'] \
                = int(os.environ['HT_REPORTING_OPA_POLL_PERIOD_SECONDS'])

        if 'HT_REPORTING_OPA_ENABLED' in os.environ:
            logger.debug("[env] Loaded HT_REPORTING_OPA_ENABLED from env")
            self.config['reporting']['opa']['enabled'] \
                = os.environ['HT_REPORTING_OPA_ENABLED'].lower() \
                == 'true'

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
            self.config['data_capture']['body_max_size_bytes'] \
                = int(os.environ['HT_DATA_CAPTURE_BODY_MAX_SIZE_BYTES'])

        # Valid values are 'TRACECONTEXT' and/or 'B3'
        if 'HT_PROPAGATION_FORMATS' in os.environ and len(os.environ['HT_PROPAGATION_FORMATS']) > 0:
            logger.debug("[env] Loaded HT_PROPAGATION_FORMATS from env")
            self.config['propagation_formats'] = os.environ['HT_PROPAGATION_FORMATS'].split(
                ',')

        if 'HT_ENABLED' in os.environ:
            logger.debug("[env] Loaded HT_ENABLED from env")
            self.config['enabled'] = os.environ['HT_ENABLED'].lower() == 'true'

        if 'HT_ENABLE_CONSOLE_SPAN_EXPORTER' in os.environ:
            logger.debug("[env] Loaded HT_ENABLE_CONSOLE_SPAN_EXPORTER from env, %s",
                         str(os.environ['HT_ENABLE_CONSOLE_SPAN_EXPORTER'].lower()))
            self.config['_use_console_span_exporter'] = \
                os.environ['HT_ENABLE_CONSOLE_SPAN_EXPORTER'].lower() == 'true'

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
            reporting.trace_reporter_type = config_pb2.TraceReporterType.ZIPKIN

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
            tmp_propagation_formats.append(config_pb2.PropagationFormat.TRACECONTEXT)
            tmp_propagation_formats = list(set(tmp_propagation_formats))
        if 'B3' in self.config['propagation_formats']:
            tmp_propagation_formats.append(config_pb2.PropagationFormat.B3)
            tmp_propagation_formats = list(set(tmp_propagation_formats))
        if not tmp_propagation_formats:
            # Default to TRACECONTEXT
            tmp_propagation_formats.append(config_pb2.PropagationFormat.TRACECONTEXT)
        self.agent_config.propagation_formats = tmp_propagation_formats
        self.agent_config.enabled = self.config['enabled']

        self.agent_config.resource_attributes = self.config['resource_attributes']

        # Validate configuration
        self.validate_config_elements(self.config, self.agent_config)

    def validate_config_elements(self, config_element, agent_config_base):
        """Validate that all present elements in the parse configuration are
        defined in the config_pb2.AgentConfig"""
        # Check for configuration entries that do not belong
        logger.debug('Entering AgentConfig.validate_config_elements().')
        for key in config_element:
            logger.debug('Checking: %s', key)
            logger.debug('type: %s', str(type(config_element[key])))
            if isinstance(config_element[key], dict):
                logger.debug('Found dictioanry. Recursing into it.')
                try:
                    if not hasattr(agent_config_base, key):
                        logger.error(
                            'Unknown attribute encountered. key=%s', key)
                        raise AttributeError
                    logger.debug('config_element=%s, agent_config_base=%s',
                                 str(config_element),
                                 str(agent_config_base))
                    if key == 'resource_attributes':
                        continue
                    self.validate_config_elements(config_element[key],
                                                  eval('agent_config_base.' + key))  # pylint: disable=W0123
                    continue
                except AttributeError as err:
                    logger.error('Unknown attribute encountered: exception=%s, stacktrace=%s',
                                 err,
                                 traceback.format_exc())
                    continue
            elif isinstance(config_element[key], (str, bool, int, list)):
                logger.debug('is string')
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
