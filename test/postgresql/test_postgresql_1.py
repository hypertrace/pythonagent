import sys
import os
import logging
import traceback
import json
import pytest
import psycopg2
from agent import Agent


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
  agent.registerPostgreSQL()
  agent.globalInit()
  #
  # End initialization logic for Python Agent
  #
  logger.info('Agent initialized.')
  
  try:
    cnx = psycopg2.connect( database='hypertrace',
                          host='localhost',
                          port=5432,
                          user='postgres',
                          password='postgres'
                        )
    cursor = cnx.cursor()
    cursor.execute("INSERT INTO hypertrace_data (col1, col2) VALUES (123, 'abcdefghijklmnopqrstuvwxyz')")
    cursor.close()
    cnx.close()
  except:
    logger.error('Failed to initialize postgresql instrumentation wrapper: exception=%s, stacktrace=%s',
      sys.exc_info()[0],
      traceback.format_exc())
    return 1
