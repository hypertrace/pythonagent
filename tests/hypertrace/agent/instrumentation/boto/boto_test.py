import os
import sys
import logging
import traceback

import moto

from hypertrace.agent import Agent
import boto.awslambda
# @pytest.mark.serial
from tests import setup_custom_logger, configure_inmemory_span_exporter


@moto.mock_lambda()
def test_run():
    logger = setup_custom_logger(__name__)
    os.environ['_HANDLER'] = 'test_lambda.example_lambda'
    agent = Agent()
    agent.instrument(None)
    memory_exporter = configure_inmemory_span_exporter(agent)

    logger.info('Running test calls.')
    lamb = boto.awslambda.connect_to_region("us-east-2")

    # multiple calls
    try:
        lamb.list_functions()
    except:
        pass

    spans = memory_exporter.get_finished_spans()
    assert spans
    assert len(spans) == 1
    span = spans[0]

    assert span.attributes['endpoint'] == 'lambda'
    assert span.attributes['http.method'] == 'GET'
    assert span.attributes['aws.region'] == 'us-east-2'
    assert span.attributes['aws.operation'] == 'list_functions'
    memory_exporter.clear()
