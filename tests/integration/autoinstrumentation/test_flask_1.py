import sys
import os
import logging
import flask
import traceback
from werkzeug.serving import make_server
import threading
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
    print('Failed to customize logger: exception=%s, stacktrace=%s',
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

def test_run():
  logger = setup_custom_logger(__name__)
  logger.info('Initializing flask app.')
  # Create Flask app
  app = Flask(__name__)
  @app.before_first_request
  def before_first_request():
    logger.debug("test_program: before_first_request() called")

  @app.route("/route1")
  def testAPI1():
    logger.info('Serving request for /route1.')
    response = flask.Response(mimetype='application/json')
    response.headers['tester3'] = 'tester3'
    response.data = str('{ "a": "a", "xyz": "xyz" }')
    return response

  logger.info('Flask app initialized.')

  server = FlaskServer(app)

  logger.info('Running test calls.')
  with app.test_client() as c:
    try: 
      logger.info('Making test call to /route1')
      r1 = app.test_client().get(
          'http://localhost:5000/route1',
          headers={ 'tester1': 'tester1',
                    'tester2':'tester2'
                  }
      )
      logger.info('Reading /route1 response.')
      a1 = r1.get_json()['a']
      assert a1 == 'a'
      logger.info('r1 result: ' + str(a1))
      return 0
    except:
      logger.error('Failed to initialize flask instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())
      raise sys.exc_info()[0]

if __name__ == '__main__':
    test_run()
