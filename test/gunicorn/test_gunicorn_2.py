import sys
import os
import logging
import traceback
import json
import pytest
import requests
from werkzeug.serving import make_server
import time
import atexit
import threading
import mysql.connector
from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import TracerProvider, export
import datetime

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
  try:
    logger = setup_custom_logger(__file__)
    logger.info('Running test calls.')
    logger.info('Making test call to /dbtest')
    startTime = datetime.datetime.now()
    for x in range(1000): # Run 1000 requests
        r1 = requests.get('http://localhost/dbtest')
        logger.info('Reading /dbtest response.')
        a1 = r1.json()['a']
        assert a1 == 'a'
        logger.info('r1 result: ' + str(a1))
    logger.info('Exiting from flask + mysql instrumentation test.')
    endTime = datetime.datetime.now()
    elapsedTime= endTime - startTime
    logger.info('elapsedTime: ' + str(elapsedTime))
    logger.info('time/request: ' + str(elapsedTime/1000))
    return 0
  except:
    logger.error('Failed to run flask + mysql instrumentation wrapper test: exception=%s, stacktrace=%s',
      sys.exc_info()[0],
      traceback.format_exc())
    raise sys.exc_info()[0]
