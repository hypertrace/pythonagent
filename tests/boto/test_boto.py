import os
import sys
import logging
import traceback
import json
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from hypertrace.agent import Agent
import boto
import boto.awslambda

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
        lamb = boto.awslambda.connect_to_region("us-east-2")

        # multiple calls
        lamb.list_functions()

        spans = memoryExporter.get_finished_spans()
        assert spans
        assert len(spans) == 1
        span = spans[0]

        assert span.attributes['endpoint'] == 'lambda'
        assert span.attributes['http.method'] == 'GET'
        assert span.attributes['aws.region'] == 'us-east-2'
        assert span.attributes['aws.operation'] == 'list_functions'
        memoryExporter.clear()

        return 0
    except:
        logger.error('Failed to test boto instrumentation wrapper: exception=%s, stacktrace=%s',
                     sys.exc_info()[0],
                     traceback.format_exc())
        raise sys.exc_info()[0]
