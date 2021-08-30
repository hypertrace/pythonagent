'''Unittest for merging config entries.'''
import os

from hypertrace.agent.config import AgentConfig
from . import DEFAULT_AGENT_CONFIG
from . import merge_config
from . import load_config_from_file


def test_merge_config() -> None:
    '''Unittest for merging config results.'''
    # set Environment Variable
    config_file_path = os.path.join(os.path.dirname(__file__), "test_agent-config.yaml")
    config_from_file = load_config_from_file(config_file_path)

    cfg = merge_config(
        DEFAULT_AGENT_CONFIG, config_from_file)

    assert cfg["service_name"] == "pythonagent_001"
    assert cfg["reporting"]["endpoint"] == "http://localhost:9411/api/v2/spans"
    assert cfg["reporting"]["trace_reporter_type"] == "ZIPKIN"
    assert cfg["reporting"]["secure"] is True
    assert cfg["reporting"]["token"] == "TestToken"
    assert cfg["reporting"]["opa"]["endpoint"] == "http://opa.traceableai:8181/"
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


def test_file_values_are_overriden_by_env() -> None:
    '''Test config is loaded from env.'''

    os.environ["HT_CONFIG_FILE"] = os.path.join(os.path.dirname(__file__), "test_agent-config.yaml")
    os.environ["HT_REPORTING_TRACE_REPORTER_TYPE"] = "OTLP"
    os.environ["HT_SERVICE_NAME"] = "test_service"

    config = AgentConfig()

    assert config.agent_config.service_name == "test_service"
    assert config.agent_config.reporting.trace_reporter_type == 2
    assert config.agent_config.reporting.endpoint == "http://localhost:9411/api/v2/spans"
    assert config.agent_config.reporting.opa.endpoint == "http://opa.traceableai:8181/"

    unset_env_variables()


def unset_env_variables():
    """Reset environment variables."""
    for key in os.environ:
        if key[0:3] == "HT_":
            del os.environ[key]
