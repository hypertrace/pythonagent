import sys
import os
import logging
import flask
import pytest
import traceback
import json
import requests
from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import TracerProvider, export
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from hypertrace.agent import Agent

os.environ['HT_PROPAGATION_FORMATS'] = 'B3'


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


def test_run():
    logger = setup_custom_logger(__name__)
    #
    # Code snippet here represents the current initialization logic
    #
    logger.info('Initializing agent.')
    agent = Agent()
    agent.register_requests()
    #
    # End initialization logic for Python Agent
    #
    logger.info('Agent initialized.')

    # Setup In-Memory Span Exporter
    logger.info('Agent initialized.')
    logger.info('Adding in-memory span exporter.')
    memoryExporter = InMemorySpanExporter()
    simpleExportSpanProcessor = SimpleSpanProcessor(memoryExporter)
    agent.register_processor(simpleExportSpanProcessor)
    logger.info('Added in-memoy span exporter')

    # Make test call
    response = requests.get('http://localhost:8002/route2')
    logger.info('response: ' + str(response))
    span_list = memoryExporter.get_finished_spans()
    # Confirm something was returned.
    assert span_list
    # Confirm there are three spans
    logger.debug('len(span_list): ' + str(len(span_list)))
    assert len(span_list) == 1
    logger.debug('span_list: ' + str(span_list[0].attributes))
    requestsSpanAsObject = json.loads(span_list[0].to_json())
    # Check that the expected results are in the flask extended span attributes
    assert requestsSpanAsObject['attributes']['http.method'] == 'GET'
    assert requestsSpanAsObject['attributes']['http.url'] == 'http://localhost:8002/route2'
    assert requestsSpanAsObject['attributes']['http.response.header.content-type'] == 'application/json'
    assert requestsSpanAsObject['attributes'][
        'http.response.body'] == '{ \"a\": \"a\", \"xyz\": \"xyz\" }'
    assert requestsSpanAsObject['attributes']['http.request.header.x-b3-traceid']
    assert requestsSpanAsObject['attributes']['http.status_code'] == 200
