import sys
import logging
import flask
import traceback
import json
import pytest
from flask import Flask
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from hypertrace.agent import Agent
from tests.django.foo.testapp.wsgi import TEST_AGENT_INSTANCE


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


memoryExporter = InMemorySpanExporter()
simpleExportSpanProcessor = SimpleSpanProcessor(memoryExporter)
TEST_AGENT_INSTANCE.register_processor(simpleExportSpanProcessor)


@pytest.mark.django_db
def test_basic_span_data(client):
    response = client.get('/test/123')
    assert response.status_code == 200

    span_list = memoryExporter.get_finished_spans()
    assert len(span_list) == 1
    django_span = span_list[0]
    assert django_span.name == 'GET test/<int:id>'
    attrs = django_span.attributes
    assert attrs["http.method"] == "GET"
    assert attrs["http.server_name"] == "testserver"
    assert attrs["http.url"] == "http://testserver/test/123"
    assert attrs["http.route"] == "test/<int:id>"

@pytest.mark.django_db
def test_collects_body_data(client):
    response = client.post('/test/123', data={"some_client_data": "123"}, content_type="application/json")
    assert response.status_code == 200

    span_list = memoryExporter.get_finished_spans()
    assert len(span_list) == 1
    django_span = span_list[0]
    assert django_span.name == 'POST test/<int:id>'
    attrs = django_span.attributes
    assert attrs["http.request.header.content-type"] == 'application/json'
    assert attrs["http.request.body"] == '{"some_client_data": "123"}'

    assert attrs["http.response.header.content-type"] == 'application/json'
    assert attrs["http.response.body"] == '{"data": 123}'




    #
    #
    # try:
    #   logger.info('Making test call to /route1')
    #   r1 = app.test_client().get('http://localhost:5000/route1', headers={ 'tester1': 'tester1', 'tester2':'tester2'})
    #   # Get all of the in memory spans that were recorded for this iteration
    #   span_list = memoryExporter.get_finished_spans()
    #   # Confirm something was returned.
    #   assert span_list
    #   # Confirm there are three spans
    #   logger.debug('len(span_list): ' + str(len(span_list)))
    #   assert len(span_list) == 1
    #   logger.debug('span_list: ' + str(span_list[0].attributes))
    #   flaskSpanAsObject = json.loads(span_list[0].to_json())
    #   # Check that the expected results are in the flask extended span attributes
    #   assert flaskSpanAsObject['attributes']['http.method'] == 'GET'
    #   assert flaskSpanAsObject['attributes']['http.target'] == '/route1'
    #   assert flaskSpanAsObject['attributes']['http.request.header.tester1'] == 'tester1'
    #   assert flaskSpanAsObject['attributes']['http.request.header.tester2'] == 'tester2'
    #   assert flaskSpanAsObject['attributes']['http.response.header.content-type'] == 'application/json'
    #   assert flaskSpanAsObject['attributes']['http.response.body'] == '{ "a": "a", "xyz": "xyz" }'
    #   assert flaskSpanAsObject['attributes']['http.status_code'] == 200
    #   assert flaskSpanAsObject['attributes']['http.response.header.tester3'] == 'tester3'
    #   memoryExporter.clear()
    #   logger.info('Making test call to /route2')
    #   r2 = app.test_client().get('http://localhost:5000/route2', headers={ 'tester1': 'tester1', 'tester2':'tester2'})
    #   # Confirm something was returned.
    #   assert span_list
    #   # Confirm there are three spans
    #   logger.debug('len(span_list): ' + str(len(span_list)))
    #   assert len(span_list) == 1
    #   logger.debug('span_list: ' + str(span_list[0].attributes))
    #   flaskSpanAsObject = json.loads(span_list[0].to_json())
    #   # Check that the expected results are in the flask extended span attributes
    #   assert flaskSpanAsObject['attributes']['http.method'] == 'GET'
    #   assert flaskSpanAsObject['attributes']['http.target'] == '/route1'
    #   assert flaskSpanAsObject['attributes']['http.request.header.tester1'] == 'tester1'
    #   assert flaskSpanAsObject['attributes']['http.request.header.tester2'] == 'tester2'
    #   assert flaskSpanAsObject['attributes']['http.response.header.content-type'] == 'application/json'
    #   assert flaskSpanAsObject['attributes']['http.response.body'] == '{ "a": "a", "xyz": "xyz" }'
    #   assert flaskSpanAsObject['attributes']['http.status_code'] == 200
    #   assert flaskSpanAsObject['attributes']['http.response.header.tester3'] == 'tester3'
    #   memoryExporter.clear()
    #   logger.info('Reading /route1 response.')
    #   a1 = r1.get_json()['a']
    #   logger.info('Reading /route2 response.')
    #   a2 = r2.get_json()['a']
    #   assert a1 == 'a'
    #   assert a2 == 'a'
    #   logger.info('r1 result: ' + str(a1))
    #   logger.info('r2 result: ' + str(a2))
    #   logger.info('Exiting from flask instrumentation test.')
    #   return 0
    # except:
    #   logger.error('Failed to initialize flask instrumentation wrapper: exception=%s, stacktrace=%s',
    #     sys.exc_info()[0],
    #     traceback.format_exc())
    #   raise sys.exc_info()[0]
