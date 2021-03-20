import sys
import os
import logging
import flask
import traceback
import json

logging.basicConfig(filename='agent.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info('Initializing agent.')
#
# Code snippet here represents the current initialization logic
#
logger.info('Initializing agent.')
agent = Agent()
agent.registerMySql()
agent.globalInit()
#
# End initialization logic for Python Agent
#
logger.info('Agent initialized.')

cnx = mysql.connector.connect(database="MySQL_Database")
cursor = cnx.cursor()
cursor.execute("INSERT INTO test (testField) VALUES (123)"
cursor.close()
cnx.close()
