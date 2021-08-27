'''Tests for file module'''
import os.path

from .file import load_config_from_file


def test_load_from_file() -> None:
    '''Unittest for merging config results.'''
    # set Environment Variable
    config_file_path = os.path.join(os.path.dirname(__file__), 'test_agent-config.yaml')
    config_from_file = load_config_from_file(config_file_path)

    cfg = config_from_file

    assert cfg["service_name"] == "pythonagent_001"
    assert cfg["reporting"]["endpoint"] == "http://localhost:9411/api/v2/spans"
    assert cfg["reporting"]["trace_reporter_type"] == "ZIPKIN"
    assert cfg["reporting"]["secure"] is True
    assert cfg["reporting"]["token"] == "TestToken"
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
