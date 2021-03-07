import sys
import logging
sys.path.append('..')
from flask import Flask
from agent import Agent

logging.basicConfig(filename='agent.log', level=logging.DEBUG,)

logging.info('Initializing flask app.')
# Create Flask app
app = Flask(__name__)
logging.info('Flask app initialized.')

#
# Code snippet here represents the current initialization logic
#
logging.info('Initializing agent.')
agent = Agent.Agent()
agent.registerFlaskApp(app)
logging.info('Agent initialized.')

#
# End initialization logic for Python Agent
#

@app.route("/")
def hello():
  logging.info('Serving request for /.')
#    tracer = trace.get_tracer(__name__)
#    with tracer.start_as_current_span("demo-request"):
#        requests.get("https://httpbin.org/anything")
  return "hello"


app.run(debug=True, port=5000)
