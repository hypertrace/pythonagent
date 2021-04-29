import sys
import os
import logging
import flask
import pytest
import traceback
import json
import requests
import aiohttp
from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import TracerProvider, export
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
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

@pytest.mark.asyncio
async def test_run():
  logger = setup_custom_logger(__name__)
  #
  # Code snippet here represents the current initialization logic
  #
  logger.info('Initializing agent.')
  agent = Agent()
  agent.register_aiohttp_client()
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

  #Make test call
  async with aiohttp.ClientSession() as session:
    async with session.post('http://localhost:8000/route2', data='{"id":0,"category":{"id":0,"name":"doggie"},"name":"doggie","photoUrls":["http://example.co"],"tags":[{"id":0,"name":"doggie"}],"status":"available"}', headers={ "Accept":"application/json", "Content-Type": "application/json", 'tester1': 'tester1', 'tester2':'tester2' }) as response:
      await response.text()
      span_list = memoryExporter.get_finished_spans()
      # Confirm something was returned.
      assert span_list
      # Confirm there are three spans
      logger.debug('len(span_list): ' + str(len(span_list)))
      assert len(span_list) == 1
      logger.debug('span_list: ' + str(span_list[0].attributes))
      aiohttpSpanAsObject = json.loads(span_list[0].to_json())
      # Check that the expected results are in the flask extended span attributes
      assert aiohttpSpanAsObject['attributes']['http.method'] == 'POST'
      assert aiohttpSpanAsObject['attributes']['http.url'] == 'http://localhost:8000/route2'
      assert aiohttpSpanAsObject['attributes']['http.request.header.tester1'] == 'tester1'
      assert aiohttpSpanAsObject['attributes']['http.request.header.tester2'] == 'tester2'
      assert aiohttpSpanAsObject['attributes']['http.response.header.content-type'] == 'application/json'
      assert aiohttpSpanAsObject['attributes']['http.request.header.traceparent']
      assert aiohttpSpanAsObject['attributes']['http.status_code'] == 200
      memoryExporter.clear()
