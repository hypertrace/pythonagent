import logging
import sys
import threading
import traceback

import flask
from flask import Flask
from flask import request, jsonify, json
from werkzeug.serving import make_server

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
agent.registerGrpc()  # Keeping this in place to test these running together
agent.globalInit()
#
# End initialization logic for Python Agent
#
logger.info('Agent initialized.')

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def before_first_request():
    logger.debug("test_program: before_first_request() called")


@app.before_request
def before_request():
    logger.debug("test_program: before_request() called")


@app.after_request
def after_request(response):
    logger.debug("test_program: after_request() called")
    return response


@app.route("/route1")
def testAPI1():
    logger.info('Serving request for /route1.')
    response = flask.Response(mimetype='application/json')
    response.headers['tester3'] = 'tester3'
    response.data = str('{ "a": "a", "xyz": "xyz" }')
    return response


@app.route("/route2")
def testAPI2():
    logger.info('Serving request for /route2.')
    response = flask.Response(mimetype='application/json')
    response.headers['tester3'] = 'tester3'
    response.data = str('{ "a": "a", "xyz": "xyz" }')
    return response


@app.route('/test/postdata', methods=['POST'])
def test_post_api():
    data = request.get_json()
    logger.info('Serving request for /test/postdata')
    response = flask.Response(mimetype='application/json')
    response.headers['tester3'] = 'tester3'
    sum1 = data['d1'] ;
    sum2 = data['d2'] ;
    response.data = str(sum1+sum2)
    return response




@app.route("/terminate")
def terminate():
    logger.info('Serving request for /terminate.')
    shutdown_server()
    response = flask.Response()
    response.data = {'a': 'a', 'xyz': 'xyz'}
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
        r1 = app.test_client().get('http://localhost:5000/route1', headers={'tester1': 'tester1', 'tester2': 'tester2'}, content_type='application/json')
        logger.info('Making test call to /route2')
        r2 = app.test_client().get('http://localhost:5000/route2', headers={'tester1': 'tester1', 'tester2': 'tester2'})
        logger.info('Making test call to /test/postdata')
        r3 = app.test_client().post('http://localhost:5000/test/postdata', headers={'tester1': 'tester1', 'tester2': 'tester2'},data=json.dumps({'d1': 10, 'd2': 20}), content_type='application/json')
        

        logger.info('Reading /route1 response')
        a1 = r1.get_json()['a']
        logger.info('Reading /route2 response')
        a2 = r2.get_json()['a']
        logger.info('Reading /test/postdata response')
        a3 = r3.status_code

        if a1 != 'a':
            logger.error('r1 Result not expected.')
            exit(1)
        if a2 != 'a':
            logger.error('r2 Result not expected.')
            exit(1)
        if a3 != 200:
            logger.error('post request to /test/postdata API has failed.')
            exit(1)

        logger.info('r1 result: ' + str(a1))
        logger.info('r2 result: ' + str(a2))
        logger.info('r3 result: ' + str(a3))
        logger.info('Exiting from flask instrumentation test.')
    except:
        e = sys.exc_info()[0]
        traceback.print_exc()
        sys.exit(1)
        os._exit(1)

sys.exit(0)