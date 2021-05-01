'''Unittest for merging config entries.'''
import os
from hypertrace.agent.config import AgentConfig
from . import DEFAULT_AGENT_CONFIG
from . import merge_config
from . import load_config_from_file
from . import config_pb2

def test_merge_config() -> None:
    '''Unittest for merging config results.'''
    # set Environment Variable
    config_file_path = "./src/hypertrace/agent/config/test_agent-config.yaml"
    config_from_file = load_config_from_file(config_file_path)

    cfg = merge_config(
        DEFAULT_AGENT_CONFIG, config_from_file)

    assert cfg["service_name"] == "pythonagent_001"
    assert cfg["reporting"]["endpoint"] == "http://localhost:9411/api/v2/spans1"
    assert cfg["reporting"]["trace_reporter_type"] == "ZIPKIN"
    assert cfg["reporting"]["secure"] is True
    assert cfg["reporting"]["token"] == "TestToken"
    assert cfg["reporting"]["opa"]["endpoint"] == "https://opa.traceableai:8181/"
    assert cfg["reporting"]["opa"]["poll_period_seconds"] == 50
    assert cfg["reporting"]["opa"]["enabled"] is True
    assert not cfg["data_capture"]["http_headers"]["request"]
    assert not cfg["data_capture"]["http_headers"]["response"]
    assert not cfg["data_capture"]["http_body"]["response"]
    assert not cfg["data_capture"]["http_body"]["response"]
    assert not cfg["data_capture"]["rpc_metadata"]["response"]
    assert not cfg["data_capture"]["rpc_metadata"]["response"]
    assert not cfg["data_capture"]["rpc_body"]["response"]
    assert not cfg["data_capture"]["rpc_body"]["response"]
    assert cfg["data_capture"]["body_max_size_bytes"] == 123457
    assert 'B3' in cfg["propagation_formats"]
    assert not cfg["enabled"]
    assert cfg["_use_console_span_exporter"] is True
    assert cfg["resource_attributes"] == {
        'tester01': 'tester01'
    }
    unset_env_variables()

def test_agent_config() -> None:
    '''Unittest functionx for agent config entries.'''
    # set Environment Variable

    unset_env_variables()

    os.environ["HT_CONFIG_FILE"] = "./src/hypertrace/agent/config/agent-config.yaml"
    print('Initializing agent.')
    config = AgentConfig()
    assert config.agent_config.service_name == "pythonagent_001"
    assert config.agent_config.reporting.endpoint == "http://localhost:9411/api/v2/spans1"
    assert config.agent_config.reporting.trace_reporter_type == 1
    assert config.agent_config.reporting.secure is True
    assert config.agent_config.reporting.token == "TestToken"
    assert config.agent_config.reporting.opa.endpoint == "https://opa.traceableai:8181/"
    assert config.agent_config.reporting.opa.poll_period_seconds == 50
    assert config.agent_config.reporting.opa.enabled is True
    assert not config.agent_config.data_capture.http_headers.request.value
    assert not config.agent_config.data_capture.http_headers.response.value
    assert not config.agent_config.data_capture.http_body.request.value
    assert not config.agent_config.data_capture.http_body.response.value
    assert not config.agent_config.data_capture.rpc_metadata.request.value
    assert not config.agent_config.data_capture.rpc_metadata.response.value
    assert not config.agent_config.data_capture.rpc_body.request.value
    assert not config.agent_config.data_capture.rpc_body.response.value
    assert config.agent_config.data_capture.body_max_size_bytes == 123457
    assert config_pb2.PropagationFormat.B3 in config.agent_config.propagation_formats
    assert not config.agent_config.enabled
    assert config.agent_config.resource_attributes == {
        'tester01': 'tester01'}
    unset_env_variables()

def test_env_config() -> None:
    '''Unittest functionx for env config entries.'''
    os.environ["HT_SERVICE_NAME"] = "pythonagent_002"
    os.environ["HT_REPORTING_ENDPOINT"] = "http://localhost:9411/api/v2/spans2"
    os.environ["HT_TRACES_EXPORTER"] = "OTLP"
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
    os.environ["HT_ENABLE_CONSOLE_SPAN_EXPORTER"] = "True"
    config = AgentConfig()
    assert config.agent_config.service_name == "pythonagent_002"
    assert config.agent_config.reporting.endpoint == "http://localhost:9411/api/v2/spans2"
    assert config.agent_config.reporting.trace_reporter_type == 2
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
    assert config_pb2.PropagationFormat.B3 in config.agent_config.propagation_formats
    assert not config.agent_config.enabled
    assert config.use_console_span_exporter()
    assert config.agent_config.resource_attributes == {
        'tester01': 'tester01'}
    unset_env_variables()

def unset_env_variables():
    """Reset environment variables."""
    for key in os.environ:
        if key[0:3] == "HT_":
            del os.environ[key]
