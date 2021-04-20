# config_pb2.Opa
'''Default values for agent-config'''
DEFAULT_OPA_ENDPOINT = 'https://localhost'  # "http://opa.traceableai:8181/"
DEFAULT_OPA_POLL_PERIOD_SECONDS = 30
DEFAULT_OPA_ENABLED = True

# config_pb2.Reporting
DEFAULT_REPORTING_TOKEN = '12345'

# config_pb2.DataCapture
DEFAULT_DATA_CAPTURE_MAX_SIZE_BYTES = 128 * 1024

# config_pb2.AgentConfig
DEFAULT_AGENT_CONFIG_ENABLED = True

DEFAULT_AGENT_CONFIG = {
    'service_name': "pythonagent",
    'reporting': {
        "endpoint": "http://localhost:9411/api/v2/spans",
        "secure": False,
        "trace_reporter_type": "ZIPKIN"
    },
    'data_capture': {
        "http_headers": {
            "request": True,
            "response": True,
        },
        "http_body": {
            "request": True,
            "response": False,
        },
        "rpc_metadata": {
            "request": True,
            "response": False,
        },
        "rpc_body": {
            "request": True,
            "response": False,
        }
    }
}

#B3,TRACECONTEXT
DEFAULT_PROPAGATION_FORMAT = 'TRACECONTEXT'
