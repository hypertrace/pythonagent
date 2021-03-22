# echo.py

import sys
import os
import logging
import flask
import traceback
from agent import Agent 
from werkzeug.serving import make_server
from flask import request
import time
import sys
import os
import atexit
import threading
from flask import Flask


logging.basicConfig(filename='agent.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

from flask import Flask           # import flask
app = Flask(__name__)             # create an app instance

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


@app.route("/")                   # at the end point /
def hello():                      # call method hello
    return "Hello World!"         # which returns "hello world"
if __name__ == "__main__":        # on running python app.py
    app.run()        
