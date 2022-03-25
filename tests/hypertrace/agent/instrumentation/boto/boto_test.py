import os
import sys
import logging
import traceback
import json
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from hypertrace.agent import Agent
import boto.awslambda

# @pytest.mark.serial
from tests import setup_custom_logger, configure_inmemory_span_exporter


def test_run():
    logger = setup_custom_logger(__name__)
    os.environ['_HANDLER'] = 'test_lambda.example_lambda'
    agent = Agent()
    agent.instrument(None)
    memory_exporter = configure_inmemory_span_exporter(agent)

    logger.info('Running test calls.')
    try:
        lamb = boto.awslambda.connect_to_region("us-east-2")

        # multiple calls
        lamb.list_functions()

        spans = memory_exporter.get_finished_spans()
        assert spans
        assert len(spans) == 1
        span = spans[0]

        assert span.attributes['endpoint'] == 'lambda'
        assert span.attributes['http.method'] == 'GET'
        assert span.attributes['aws.region'] == 'us-east-2'
        assert span.attributes['aws.operation'] == 'list_functions'
        memory_exporter.clear()

        return 0
    except:
        logger.error('Failed to test boto instrumentation wrapper: exception=%s, stacktrace=%s',
                     sys.exc_info()[0],
                     traceback.format_exc())
        raise sys.exc_info()[0]
