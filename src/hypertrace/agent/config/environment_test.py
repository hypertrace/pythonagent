'''Environment config test'''

import os
from .environment import load_config_from_env


def test_env_config() -> None:
    '''Test config is loaded from env.'''
    os.environ["HT_SERVICE_NAME"] = "pythonagent_002"
    os.environ["HT_REPORTING_ENDPOINT"] = "http://localhost:9411/api/v2/spans2"
    os.environ["HT_REPORTING_TRACE_REPORTER_TYPE"] = "OTLP"
    os.environ["HT_REPORTING_SECURE"] = "True"
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
    os.environ["HT_PROPAGATION_FORMATS"] = "B3,TRACECONTEXT"
    os.environ["HT_ENABLED"] = "False"
    os.environ["HT_ENABLE_CONSOLE_SPAN_EXPORTER"] = "True"
    config = load_config_from_env()
    print(config)
    assert config['service_name'] == "pythonagent_002"
    assert config['reporting']['endpoint'] == "http://localhost:9411/api/v2/spans2"
    assert config['reporting']['trace_reporter_type'] == 'OTLP'
    assert config['reporting']['secure'] is True
    assert config['reporting']['opa']['endpoint'] == "https://opa.traceableai:8181/"
    assert config['reporting']['opa']['poll_period_seconds'] == 50
    assert config['reporting']['opa']['enabled'] is False
    assert config['data_capture']['http_headers']['request'] is False
    assert config['data_capture']['http_headers']['response'] is False
    assert config['data_capture']['http_body']['request'] is False
    assert config['data_capture']['http_body']['response'] is False
    assert config['data_capture']['rpc_metadata']['request'] is False
    assert config['data_capture']['rpc_metadata']['response'] is False
    assert config['data_capture']['rpc_body']['request'] is False
    assert config['data_capture']['rpc_body']['response'] is False
    assert config['data_capture']['body_max_size_bytes'] == 123456
    assert 'B3' in config['propagation_formats']
    assert 'TRACECONTEXT' in config['propagation_formats']
    assert config['enabled'] is False
    assert config['_use_console_span_exporter']
    unset_env_variables()


def unset_env_variables():
    """Reset environment variables."""
    for key in os.environ:
        if key[0:3] == "HT_":
            del os.environ[key]
