import sys
import os
import logging
import traceback
import json
import psycopg2
from agent import Agent

logging.basicConfig(filename='agent.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
  e = sys.exc_info()[0]
  traceback.print_exc()
  sys.exit(1)
  os._exit(1)
