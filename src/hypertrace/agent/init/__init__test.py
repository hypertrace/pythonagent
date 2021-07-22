"""Agent init test"""
from hypertrace.agent import Agent
from hypertrace.agent.config import config_pb2

def test_edit_config() -> None:
    """Test programmatic editing of config values"""
    agent = Agent()
    with agent.edit_config() as config:
        config.service_name = "test service name"

        config.reporting.endpoint = 'http://localhost:4317'
        config.reporting.trace_reporter_type = config_pb2.TraceReporterType.OTLP

        config.propagation_formats = [config_pb2.PropagationFormat.B3]

        config.data_capture.http_headers.request.value = False
        config.data_capture.http_headers.response.value = False
        config.data_capture.http_body.request.value = True
        config.data_capture.http_body.response.value = False
        config.data_capture.rpc_metadata.request.value = False
        config.data_capture.rpc_metadata.response.value=True
        config.data_capture.rpc_body.request.value = True
        config.data_capture.rpc_body.response.value = True
        config.data_capture.body_max_size_bytes = 256000

    agent_config = agent._config.agent_config  # pylint:disable=W0212
    assert agent_config

    reporting = agent_config.reporting
    assert reporting.endpoint == 'http://localhost:4317'
    assert reporting.trace_reporter_type == config_pb2.TraceReporterType.OTLP

    assert len(agent_config.propagation_formats) == 1
    assert agent_config.propagation_formats[0] == config_pb2.PropagationFormat.B3

    data_capture = agent_config.data_capture
    assert not data_capture.http_headers.request.value
    assert not data_capture.http_headers.response.value

    assert data_capture.http_body.request.value
    assert not data_capture.http_body.response.value

    assert not data_capture.rpc_metadata.request.value
    assert data_capture.rpc_metadata.response.value

    assert data_capture.rpc_body.request.value
    assert data_capture.rpc_body.response.value

    assert data_capture.body_max_size_bytes == 256000
