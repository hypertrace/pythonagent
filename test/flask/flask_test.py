import sys
import os
import logging
import flask
import traceback
from werkzeug.serving import make_server
from flask import request
import time
import atexit
import threading
from flask import Flask
from agent import Agent
logging.basicConfig(filename='agent.log', level=logging.DEBUG,)

logging.info('Initializing flask app.')
# Create Flask app
app = Flask(__name__)
logging.info('Flask app initialized.')

logging.info('Initializing agent.')
#
# Code snippet here represents the current initialization logic
#
logging.info('Initializing agent.')
agent = Agent()
agent.registerFlaskApp(app)
agent.registerGrpc() # Keeping this in place to test these running together
agent.globalInit()
#
# End initialization logic for Python Agent
#
logging.info('Agent initialized.')

def before_first_request():
  logging.debug("test_program: before_first_request() called")

@app.before_request
def before_request():
    logging.debug("test_progam: before_request() called")

@app.after_request
def after_request(response):
    logging.debug("test_program: after_request() called")
    return response

@app.route("/route1")
def testAPI1():
  logging.info('Serving request for /route1.')
  response = flask.Response(mimetype='application/json')
  response.headers['tester3'] = 'tester3'
  response.data = str('{ "a": "a", "xyz": "xyz" }')
  return response

@app.route("/route2")
def testAPI2():
  logging.info('Serving request for /route2.')
  response = flask.Response(mimetype='application/json')
  response.headers['tester3'] = 'tester3'
  response.data = str('{ "a": "a", "xyz": "xyz" }')
  return response

@app.route("/terminate")
def terminate():
  logging.info('Serving request for /terminatae.')
  shutdown_server()
  response = flask.Response()
  response.data = { 'a': 'a', 'xyz': 'xyz' }
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
    logging.info('starting server.')
    self.srv.serve_forever()
    self.start()

  def shutdown(self):
    logging.info('Shutting down server.')
    self.srv.shutdown()

server = FlaskServer(app)

logging.info('Running test calls.')
with app.test_client() as c:
  try: 
    logging.info('Making test call to /route1')
    r1 = app.test_client().get('http://localhost:5000/route1', headers={ 'tester1': 'tester1', 'tester2':'tester2'})
    logging.info('Making test call to /route2')
    r2 = app.test_client().get('http://localhost:5000/route2', headers={ 'tester1': 'tester1', 'tester2':'tester2'})
    logging.info('Reading /route1 response.')
    a1 = r1.get_json()['a']
    logging.info('Reading /route2 response.')
    a2 = r2.get_json()['a']
    if a1 != 'a':
      logging.error('r1 Result not expected.')
      exit(1)
    if a2 != 'a':
      logging.error('r2 Result not expected.')
      exit(1)
    logging.info('r1 result: ' + str(a1))
    logging.info('r2 result: ' + str(a2))
    logging.info('Exiting from flask instrumentation test.')
  except:
    e = sys.exc_info()[0]
    traceback.print_exc() 
    sys.exit(1)
    os._exit(1)

sys.exit(0)
