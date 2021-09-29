import sys
import os
import logging
import traceback
import json
import pytest
import mysql.connector
from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import TracerProvider, export
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from hypertrace.agent import Agent


def fail_test():
    raise RuntimeError('Error')


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
        logger.error('Failed to customize logger: exception=%s, stacktrace=%s',
                     sys.exc_info()[0],
                     traceback.format_exc())


def test_run():
    logger = setup_custom_logger(__name__)
    logger.info('Initializing agent.')
    #
    # Code snippet here represents the current initialization logic
    #
    logger.info('Initializing agent.')
    agent = Agent()
    agent.instrument()
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

    try:
        logger.info('Making connection to mysql.')
        cnx = mysql.connector.connect(database='hypertrace',
                                      username='root',
                                      password='root',
                                      host='localhost',
                                      port=3306)
        logger.info('Connect successfully.')
        cursor = cnx.cursor()
        logger.info('Running INSERT statement.')
        cursor.execute(
            "INSERT INTO hypertrace_data (col1, col2) VALUES (123, 'abcdefghijklmnopqrstuvwxyz')")
        logger.info('Statement ran successfully')
        logger.info('Closing cursor.')
        cursor.close()
        logger.info('Closing connection.')
        cnx.close()
        logger.info('Connection closed.')
        # Get all of the in memory spans that were recorded for this iteration
        span_list = memoryExporter.get_finished_spans()
        # Confirm something was returned.
        assert span_list
        # Confirm there are three spans
        logger.debug('len(span_list): ' + str(len(span_list)))
        assert len(span_list) == 1
        logger.debug('span_list: ' + str(span_list[0].attributes))
        flaskSpanAsObject = json.loads(span_list[0].to_json())
        assert flaskSpanAsObject['attributes']['db.system'] == 'mysql'
        assert flaskSpanAsObject['attributes']['db.name'] == 'hypertrace'
        assert flaskSpanAsObject['attributes'][
            'db.statement'] == "INSERT INTO hypertrace_data (col1, col2) VALUES (123, 'abcdefghijklmnopqrstuvwxyz')"
        assert flaskSpanAsObject['attributes']['db.user'] == 'root'
        assert flaskSpanAsObject['attributes']['net.peer.name'] == 'localhost'
        assert flaskSpanAsObject['attributes']['net.peer.port'] == 3306

        fail_test()
    except Exception as e:
        assert type(e) is RuntimeError
