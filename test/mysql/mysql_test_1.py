import sys
import os
import logging
import traceback
import json
import mysql.connector
from agent import Agent

logging.basicConfig(filename='agent.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info('Initializing agent.')
#
# Code snippet here represents the current initialization logic
#
logger.info('Initializing agent.')
agent = Agent()
agent.registerMySQL()
agent.globalInit()
#
# End initialization logic for Python Agent
#
logger.info('Agent initialized.')

cnx = mysql.connector.connect(database="db", username='mysql', password='mysql', host='localhost', port=3306)
cursor = cnx.cursor()
cursor.execute("INSERT INTO test (testField) VALUES (123)")
cursor.close()
cnx.close()
