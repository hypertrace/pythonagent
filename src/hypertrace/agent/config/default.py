DEFAULT_AGENT_CONFIG = {
    '_use_console_span_exporter': False,
    'agent_config_enabled' : True,
    'hypertrace_enabled': True,
    'propagation_formats':'TRACECONTEXT',
    'opa_endpoint': '',
    'opa_poll_period_seconds':'',
    'data_capture_max_size_bytes':'',
    'opa_enabled' : '',
    'reporting_token':'',
    'service_name': '',
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