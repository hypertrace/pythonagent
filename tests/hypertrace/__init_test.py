from hypertrace.agent import Agent
from hypertrace.agent.config import AgentConfig
from hypertrace.agent.config import config_pb2 as hypertrace_config


def test_edit_config():
    agent = Agent()
    with agent.edit_config() as config:
        config.service_name = "some new service name"
        config.reporting.endpoint = "http://localhost:4317"
        config.reporting.trace_reporter_type = hypertrace_config.TraceReporterType.OTLP
        config.propagation_formats = [hypertrace_config.PropagationFormat.B3]

    assert agent._config.agent_config.reporting.trace_reporter_type \
           is hypertrace_config.TraceReporterType.OTLP  # pylint:disable=W0212
    assert agent._config.agent_config.propagation_formats == [
        hypertrace_config.PropagationFormat.B3]  # pylint:disable=W0212
    assert agent._config.agent_config.service_name == "some new service name"  # pylint:disable=W0212

    err = None
    try:
        agent.instrument()
    except Exception as e:
        err = e

    assert err is None