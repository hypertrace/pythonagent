'''The default configuration for pythonagent'''
DEFAULT_AGENT_CONFIG = {
    '_use_console_span_exporter': False,
    'enabled': True,
    'propagation_formats': ['TRACECONTEXT'],
    'service_name': 'pythonagent',
    'reporting': {
        'endpoint': 'http://localhost:4317',
        'secure': False,
        'trace_reporter_type': 'OTLP',
        'token': '',
        'opa': {
            'endpoint': 'http://opa.traceableai:8181/',
            'poll_period_seconds': 60,
            'enabled': False,
        }
    },
    'data_capture': {
        'http_headers': {
            'request': True,
            'response': True,
        },
        'http_body': {
            'request': True,
            'response': True,
        },
        'rpc_metadata': {
            'request': True,
            'response': True,
        },
        'rpc_body': {
            'request': True,
            'response': True,
        },
        'body_max_size_bytes': 131072
    },
    'resource_attributes': {}
}
