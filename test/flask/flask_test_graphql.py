import sys
import os
import logging
import flask
import traceback
import json
from werkzeug.serving import make_server
from flask import request
import time
import atexit
import threading
from flask import Flask
from agent import Agent

logging.basicConfig(filename='agent.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info('Initializing flask app.')
# Create Flask app
app = Flask(__name__)
logger.info('Flask app initialized.')

logger.info('Initializing agent.')
#
# Code snippet here represents the current initialization logic
#
logger.info('Initializing agent.')
agent = Agent()
agent.registerFlaskApp(app)
agent.registerGrpc() # Keeping this in place to test these running together
agent.globalInit()
#
# End initialization logic for Python Agent
#
logger.info('Agent initialized.')

def before_first_request():
  logger.debug("test_program: before_first_request() called")

@app.before_request
def before_request():
    logger.debug("test_progam: before_request() called")

@app.after_request
def after_request(response):
    logger.debug("test_program: after_request() called")
    return response

@app.route("/route1")
def testAPI1():
  logger.info('Serving request for /route1.')
  response = flask.Response(mimetype='application/graphql')
  response.headers['tester3'] = 'tester3'
  response.data = str('''{
  "errors": [
    {
      "message": "Name for character with ID 1002 could not be fetched.",
      "locations": [ { "line": 6, "column": 7 } ],
      "path": [ "hero", "heroFriends", 1, "name" ]
    }
  ],
  "data": {
    "hero": {
      "name": "R2-D2",
      "heroFriends": [
        {
          "id": "1000",
          "name": "Luke Skywalker"
        },
        {
          "id": "1002",
          "name": null
        },
        {
          "id": "1003",
          "name": "Leia Organa"
        }
      ]
    }
  }
}''').replace('\n','')
  return response

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

  def shutdown(self):
    logger.info('Shutting down server.')
    self.srv.shutdown()

server = FlaskServer(app)

logger.info('Running test calls.')
with app.test_client() as c:
  try: 
    logger.info('Making test call to /route1')
    r1 = c.get('http://localhost:5000/route1', headers={ 'tester1': 'tester1', 'tester2':'tester2'})
    a1 = json.loads(r1.data.decode('UTF8'))['data']['hero']['name']
    logger.info('Reading /route1 response: ' + str(a1))
    if a1 != 'R2-D2':
      logger.error('r1 Result not expected.')
      exit(1)
    logger.info('r1 result: ' + str(a1))
    logger.info('Exiting from flask instrumentation test.')
  except:
    e = sys.exc_info()[0]
    traceback.print_exc() 
    sys.exit(1)
    os._exit(1)

sys.exit(0)
