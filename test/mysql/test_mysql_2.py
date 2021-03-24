import sys
import os
import logging
import traceback
import json
import pytest
import flask
from werkzeug.serving import make_server
from flask import request
import time
import atexit
import threading
import mysql.connector
from agent import Agent
from flask import Flask

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

# Run the flask web server in a separate thread
class FlaskServer(threading.Thread):
  def __init__(self, app):
    super().__init__()
    self.daemon = True
    threading.Thread.__init__(self)
    self.srv = make_server('localhost', 5000, app)
    self.ctx = app.app_context()
    self.ctx.push()

  def run(self):
    logger.info('starting server.')
    self.srv.serve_forever()
    self.start()

@pytest.mark.serial
def test_run():
  logger = setup_custom_logger(__name__)
  logger.info('Initializing flask app.')
  # Create Flask app
  app = Flask(__name__)

  @app.route("/dbtest")
  def testAPI1():
    try:
      logger.info('Serving request for /dbtest.')
      logger.info('Making connection to mysql.')
      cnx = mysql.connector.connect(database='hypertrace',
        username='root',
        password='example',
        host='localhost',
        port=3306)
      logger.info('Connect successfully.')
      cursor = cnx.cursor()
      logger.info('Running INSERT statement.')
      cursor.execute("INSERT INTO hypertrace_data (col1, col2) VALUES (123, 'abcdefghijklmnopqrstuvwxyz')")
      cursor.execute("INSERT INTO hypertrace_data (col1, col2) VALUES (456, 'abcdefghijklmnopqrstuvwxyz')")
      logger.info('Statement ran successfully')
      logger.info('Closing cursor.')
      cursor.close()
      logger.info('Closing connection.')
      cnx.close()
      logger.info('Connection closed.')
      response = flask.Response(mimetype='application/json')
      response.data = str('{ "a": "a", "xyz": "xyz" }')
      return response
    except:
      logger.error('Failed to initialize postgresql instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      response = flask.Response(mimetype='application/json')
      response.data = str('{}')
      return response

  logger.info('Flask app initialized.')

  logger.info('Initializing agent.')
  #
  # Code snippet here represents the current initialization logic
  #
  logger.info('Initializing agent.')
  agent = Agent()
  agent.registerFlaskApp(app)
  agent.registerMySQL() 
  agent.globalInit()
  #
  # End initialization logic for Python Agent
  #
  logger.info('Agent initialized.')

  server = FlaskServer(app)

  logger.info('Running test calls.')
  with app.test_client() as c:
    try:
      logger.info('Making test call to /route1')
      for x in range(10): # Run 10 requests
        r1 = app.test_client().get('http://localhost:5000/dbtest')
        logger.info('Reading /route1 response.')
        a1 = r1.get_json()['a']
        assert a1 == 'a'
        logger.info('r1 result: ' + str(a1))
      logger.info('Exiting from flask instrumentation test.')
      return 0
    except:
      logger.error('Failed to initialize postgresql instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      return 1
