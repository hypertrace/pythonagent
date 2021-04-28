import sys
import logging
import flask
import traceback
from werkzeug.serving import make_server
import threading
from hypertrace.agent import Agent

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

logger = setup_custom_logger(__name__)


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


def test_run():
    logger.info('Initializing flask app.')

    # Create Flask app
    app = flask.Flask(__name__)

    @app.before_first_request
    def before_first_request():
        logger.debug("test_program: before_first_request() called")

    @app.before_request
    def before_request():
        logger.debug("test_progam: before_request() called")

    @app.after_request
    def after_request(response):
        logger.debug("test_program: after_request() called")
        return response

    @app.route('/', methods=['OPTIONS'])
    def test_api_1():
        logger.info('Serving request for OPTIONS /')
        response = flask.Response()
        response.headers['Allow'] = ['OPTIONS']
        return response

    logger.info('Flask app initialized.')
    #
    # Code snippet here represents the current initialization logic
    #
    logger.info('Initializing agent.')
    agent = Agent(True)
    agent.register_flask_app(app)
    #
    # End initialization logic for Python Agent
    #
    logger.info('Agent initialized.')

    logger.info('Server initialized')
    FlaskServer(app)

    logger.info('Running test calls.')
    with app.test_client():
        try:
            logger.info('Making OPTIONS call to /')
            r1 = app.test_client().options('http://localhost:5000/')
            assert r1.headers['Allow'] == "['OPTIONS']"
        except:
            logger.error('Failed to initialize flask instrumentation wrapper: exception=%s, stacktrace=%s',
                         sys.exc_info()[0],
                         traceback.format_exc())
            raise sys.exc_info()[0]
