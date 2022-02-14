import os
import sys
import logging
import traceback
import json
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from hypertrace.agent import Agent


def setup_custom_logger(name):
    try:
        formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        handler = logging.FileHandler('agent.log', mode='a')
        handler.setFormatter(formatter)
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.addHandler(screen_handler)
        return logger
    except:
        print('Failed to customize logger: exception=%s, stacktrace=%s',
              sys.exc_info()[0],
              traceback.format_exc())


def example_lambda(event, context):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"test_key": "test_value"})
    }


class ContextStub:
    def __init__(self):
        self.invoked_function_arn = '123'
        self.aws_request_id = 56789


# @pytest.mark.serial
def test_run():
    logger = setup_custom_logger(__name__)
    os.environ['_HANDLER'] = 'test_lambda.example_lambda'
    agent = Agent()
    agent.instrument(None)

    # Setup In-Memory Span Exporter
    logger.info('Agent initialized.')
    logger.info('Adding in-memory span exporter.')
    memoryExporter = InMemorySpanExporter()
    simpleExportSpanProcessor = SimpleSpanProcessor(memoryExporter)
    agent.register_processor(simpleExportSpanProcessor)
    logger.info('Added in-memory span exporter')

    logger.info('Running test calls.')
    try:
        mockEventData = {'version': '2.0', 'routeKey': 'POST /test-function', 'rawPath': '/default/test-function',
                         'rawQueryString': '',
                         'headers': {'accept': '*/*', 'content-length': '23', 'content-type': 'application/json',
                                     'host': 'something.foo.bar',
                                     'user-agent': 'insomnia/2021.6.0',
                                     'x-amzn-trace-id': 'Root=1-61bc2935-0d71070e0218146e5683cd7e',
                                     'x-forwarded-for': '202.87.208.0, 207.255.222.177', 'x-forwarded-port': '443',
                                     'x-forwarded-proto': 'https'},
                         'multiValueHeaders': {
                             'accept': [
                                 '*/*'
                             ],
                             'cookie': [
                                 'foo=bar;something=another-cookie'
                             ],
                             'Host': [
                                 'something.foo.bar'
                             ],
                             'User-Agent': [
                                 'insomnia/2021.7.2'
                             ],
                             'X-Amzn-Trace-Id': [
                                 'Root=1-61bc2935-0d71070e0218146e5683cd7e'
                             ],
                             'X-Forwarded-For': [
                                 '202.87.208.0, 207.255.222.177'
                             ],
                             'X-Forwarded-Port': [
                                 '443'
                             ],
                             'X-Forwarded-Proto': [
                                 'https'
                             ]
                         },
                         'requestContext': {'accountId': '286278240186', 'apiId': 'brz7ycf4q7',
                                            'domainName': 'something.foo.bar',
                                            'domainPrefix': 'brz7ycf4q7',
                                            'http': {'method': 'POST', 'path': '/default/test-function',
                                                     'protocol': 'HTTP/1.1', 'sourceIp': '207.255.222.177',
                                                     'userAgent': 'insomnia/2021.6.0'}, 'requestId': 'Ketgdj-vCYcEMHw=',
                                            'routeKey': 'POST /test-function', 'stage': 'default',
                                            'time': '17/Dec/2021:06:07:49 +0000', 'timeEpoch': 1639721269962},
                         'body': '{\n\t"name": "sample body data"\n}', 'isBase64Encoded': False}

        cntxt = ContextStub()
        example_lambda(mockEventData, cntxt)
        # Get all of the in memory spans that were recorded for this iteration
        span_list = memoryExporter.get_finished_spans()
        # Confirm something was returned.
        assert span_list

        assert len(span_list) == 1
        logger.debug('span_list: ' + str(span_list[0].attributes))
        span = json.loads(span_list[0].to_json())
        # Check that the expected results are in the flask extended span attributes
        assert span['attributes']['http.method'] == 'POST'
        assert span['attributes']['http.host'] == 'something.foo.bar'
        assert span['attributes']['http.target'] == '/default/test-function'
        assert span['attributes']['http.request.header.x-forwarded-for'] == '202.87.208.0, 207.255.222.177'
        assert span['attributes']['http.request.header.x-amzn-trace-id'] == 'Root=1-61bc2935-0d71070e0218146e5683cd7e'
        assert span['attributes']['http.request.header.cookie'] == 'foo=bar;something=another-cookie'
        assert span['attributes']['http.response.header.content-type'] == 'application/json'
        assert span['attributes']['http.request.body'] == '{\n\t"name": "sample body data"\n}'
        assert span['attributes']['http.response.body'] == '{"test_key": "test_value"}'
        assert span['attributes']['http.status_code'] == 200
        assert span['attributes']['http.response.header.content-type'] == 'application/json'
        memoryExporter.clear()

        return 0
    except:
        logger.error('Failed to initialize lambda instrumentation wrapper: exception=%s, stacktrace=%s',
                     sys.exc_info()[0],
                     traceback.format_exc())
        raise sys.exc_info()[0]
