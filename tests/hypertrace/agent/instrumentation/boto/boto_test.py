import os
import logging

import boto3
import moto

from hypertrace.agent import Agent
from tests import setup_custom_logger, configure_inmemory_span_exporter


@moto.mock_lambda
def test_run():
    # Setup logger and environment variables
    logger = setup_custom_logger(__name__)
    os.environ['_HANDLER'] = 'test_lambda.example_lambda'

    # Initialize the agent and memory exporter
    agent = Agent()
    agent.instrument(None)
    memory_exporter = configure_inmemory_span_exporter(agent)

    # Create a mock Lambda client with boto3
    lambda_client = boto3.client('lambda', region_name="us-east-2")

    # Log the test execution
    logger.info('Running test calls.')

    # Mock Lambda interaction
    try:
        response = lambda_client.list_functions()
        logger.info("List functions response: %s", response)
    except Exception as e:
        logger.error("Lambda list_functions failed: %s", e)

    # Validate the spans
    spans = memory_exporter.get_finished_spans()
    assert spans, "No spans were captured"
    assert len(spans) == 1, "Expected exactly one span"

    span = spans[0]
    assert span.attributes['rpc.service'] == 'Lambda'
    assert span.attributes['aws.region'] == 'us-east-2'
    assert span.attributes['rpc.method'] == 'ListFunctions'

    # Clear the memory exporter for further tests
    memory_exporter.clear()
