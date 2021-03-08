import sys
import logging
import flask
sys.path.append('..')
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
agent = Agent.Agent()
agent.registerFlaskApp(app)
#
# End initialization logic for Python Agent
#
logging.info('Agent initialized.')

@app.route("/")
def testAPI():
  logging.info('Serving request for /.')
  response = flask.Response()
  response.headers['tester3'] = 'tester3' 
  response.data = str({ 'a': 'a', 'xyz': 'xyz' })
  return response

app.run(debug=True, port=5000)
