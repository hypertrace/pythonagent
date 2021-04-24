'''Unittest for merging config entries.'''
from . import merge_config

def test_merge_config():
    '''Unittest function for merging config entries.'''
    cfg = merge_config({
        'reporting': {
            "endpoint": "http://localhost:9411/api/v2/spans",
            "trace_reporter_type": "ZIPKIN",
            "secure": False
        },
        'propagation_formats': ['B3', 'TRACECONTEXT']
    }, {
        "service_name": "myservice",
        'reporting': {
            "endpoint": "https://myhost:9411/api/v2/spans",
            "secure": True
        },
    })

    assert cfg["service_name"] == "myservice"
    assert cfg["reporting"]["endpoint"] == "https://myhost:9411/api/v2/spans"
    assert cfg["reporting"]["trace_reporter_type"] == "ZIPKIN"
