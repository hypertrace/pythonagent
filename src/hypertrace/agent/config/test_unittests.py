'''Unittest for merging config entries.'''
import os
from hypertrace.agent.config import AgentConfig
from . import merge_config
from . import load_config_from_file
from . import DEFAULT_AGENT_CONFIG


def test_merge_config():
    '''Unittest functionx for merging config entries.'''
    # set Environment Variable
    os.environ["HT_CONFIG_FILE"] = "./src/hypertrace/agent/config/agent-config.yaml"
    config_from_file = load_config_from_file(
        os.environ['HT_CONFIG_FILE'])

    cfg = merge_config(
        DEFAULT_AGENT_CONFIG, config_from_file)

    assert cfg["service_name"] == "pythonagent_001"
    assert cfg["reporting"]["endpoint"] == "http://localhost:9411/api/v2/spans1"
    assert cfg["reporting"]["trace_reporter_type"] == "ZIPKIN"
    assert cfg["reporting"]["secure"] is True
    assert cfg["reporting"]["token"] == ""
    assert cfg["reporting"]["opa"]["endpoint"] == "http://opa.traceableai:8181/"
    assert cfg["reporting"]["opa"]["poll_period_seconds"] == 60
    assert not cfg["reporting"]["opa"]["enabled"]
    assert not cfg["data_capture"]["http_headers"]["request"]
    assert not cfg["data_capture"]["http_headers"]["response"]
    assert not cfg["data_capture"]["http_body"]["response"]
    assert not cfg["data_capture"]["http_body"]["response"]
    assert not cfg["data_capture"]["rpc_metadata"]["response"]
    assert not cfg["data_capture"]["rpc_metadata"]["response"]
    assert not cfg["data_capture"]["rpc_body"]["response"]
    assert not cfg["data_capture"]["rpc_body"]["response"]
    assert cfg["data_capture"]["body_max_size_bytes"] == 131072
    assert cfg["propagation_formats"] == "B3"
    assert not cfg["enabled"]
    assert cfg["_use_console_span_exporter"] is True
    assert cfg["resource_attributes"] == {}


def test_agent_config():
    '''Unittest functionx for agent config entries.'''
    # set Environment Variable
    os.environ["HT_CONFIG_FILE"] = "./src/hypertrace/agent/config/agent-config.yaml"
    print('Initializing agent.')
    config = AgentConfig()
    assert config.agent_config.service_name == "pythonagent_001"
    assert config.agent_config.reporting.endpoint == "http://localhost:9411/api/v2/spans1"
    assert config.agent_config.reporting.trace_reporter_type == 0
    assert config.agent_config.reporting.secure is True
    assert config.agent_config.reporting.token == ""
    assert config.agent_config.reporting.opa.endpoint == "http://opa.traceableai:8181/"
    assert config.agent_config.reporting.opa.poll_period_seconds == 60
    assert not config.agent_config.reporting.opa.enabled
    assert not config.agent_config.data_capture.http_headers.request.value
    assert not config.agent_config.data_capture.http_headers.response.value
    assert not config.agent_config.data_capture.http_body.request.value
    assert not config.agent_config.data_capture.http_body.response.value
    assert not config.agent_config.data_capture.rpc_metadata.request.value
    assert not config.agent_config.data_capture.rpc_metadata.response.value
    assert not config.agent_config.data_capture.rpc_body.request.value
    assert not config.agent_config.data_capture.rpc_body.response.value
    assert config.agent_config.data_capture.body_max_size_bytes == 131072
    assert config.agent_config.propagation_formats == 0
    assert not config.agent_config.enabled
    assert config.agent_config.resource_attributes == {'service_name': 'pythonagent_001'}


def test_env_config():
    '''Unittest functionx for env config entries.'''
    print('Initializing agent.')
    os.environ["HT_SERVICE_NAME"] = "pythonagent_002"
    os.environ["HT_REPORTING_ENDPOINT"] = "http://localhost:9411/api/v2/spans2"
    os.environ["HT_TRACES_EXPORTER"] = "Zikpin"
    os.environ["HT_REPORTING_SECURE"] = "True"
    os.environ["HT_REPORTING_TOKEN"] = ""
    os.environ["HT_REPORTING_OPA_ENDPOINT"] = "https://opa.traceableai:8181/"
    os.environ["HT_REPORTING_OPA_POLL_PERIOD_SECONDS"] = "50"
    os.environ["HT_REPORTING_OPA_ENABLED"] = "False"
    os.environ["HT_DATA_CAPTURE_HTTP_HEADERS_REQUEST"] = "False"
    os.environ["HT_DATA_CAPTURE_HTTP_HEADERS_RESPONSE"] = "False"
    os.environ["HT_DATA_CAPTURE_HTTP_BODY_REQUEST"] = "False"
    os.environ["HT_DATA_CAPTURE_HTTP_BODY_RESPONSE"] = "False"
    os.environ["HT_DATA_CAPTURE_RPC_METADATA_REQUEST"] = "False"
    os.environ["HT_DATA_CAPTURE_RPC_METADATA_RESPONSE"] = "False"
    os.environ["HT_DATA_CAPTURE_RPC_BODY_REQUEST"] = "False"
    os.environ["HT_DATA_CAPTURE_RPC_BODY_RESPONSE"] = "False"
    os.environ["HT_DATA_CAPTURE_BODY_MAX_SIZE_BYTES"] = "123456"
    os.environ["HT_PROPAGATION_FORMATS"] = "B3"
    os.environ["HT_ENABLED"] = "False"
    os.environ["HT_ENABLE_CONSOLE_SPAN_EXPORTER"] = "{'service_name': 'pythonagent_002'}"
    config = AgentConfig()
    assert config.agent_config.service_name == "pythonagent_002"
    assert config.agent_config.reporting.endpoint == "http://localhost:9411/api/v2/spans2"
    assert config.agent_config.reporting.trace_reporter_type == 0
    assert config.agent_config.reporting.secure is True
    assert config.agent_config.reporting.token == ""
    assert config.agent_config.reporting.opa.endpoint == "https://opa.traceableai:8181/"
    assert config.agent_config.reporting.opa.poll_period_seconds == 50
    assert not config.agent_config.reporting.opa.enabled
    assert not config.agent_config.data_capture.http_headers.request.value
    assert not config.agent_config.data_capture.http_headers.response.value
    assert not config.agent_config.data_capture.http_body.request.value
    assert not config.agent_config.data_capture.http_body.response.value
    assert not config.agent_config.data_capture.rpc_metadata.request.value
    assert not config.agent_config.data_capture.rpc_metadata.response.value
    assert not config.agent_config.data_capture.rpc_body.request.value
    assert not config.agent_config.data_capture.rpc_body.response.value
    assert config.agent_config.data_capture.body_max_size_bytes == 123456
    assert config.agent_config.propagation_formats == 0
    assert not config.agent_config.enabled
    assert config.agent_config.resource_attributes == {'service_name': 'pythonagent_002'}
