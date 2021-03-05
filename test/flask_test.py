# File: flask_test.py
# Author: Nitin Sahai
# Date: 03/04/2021
# Notes:
#
# Issue2 - Working example of python opentelemetry agent.
#
import sys
sys.path.append('..')
from flask import Flask

# Create Flask app
app = Flask(__name__)

#
# Code snippet here represents the current initialization logic
#
from agent import Agent
agent = Agent.Agent()
agent.registerFlaskApp(app)
#
# End initialization logic for Python Agent
#

@app.route("/")
def hello():
#    tracer = trace.get_tracer(__name__)
#    with tracer.start_as_current_span("demo-request"):
#        requests.get("https://httpbin.org/anything")
    return "hello"


app.run(debug=True, port=5000)
