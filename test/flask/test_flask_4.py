import sys
import logging
import flask
import traceback
import json
from werkzeug.serving import make_server
import threading
from agent import Agent


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

    # Used for storing users for this test
    users = {}

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

    @app.route('/', methods=['PUT'])
    def test_api_1():
        logger.info('Serving request for PUT /')
        data = flask.request.get_json()
        logger.info(data)
        response = flask.Response(mimetype='application/json')
        response.data = json.dumps(data)

        if 'id' in data and data['id'] in users:
            logger.debug('User exists, will modify it.')
            updated_data = data.copy()
            # data['id'] can't be modified
            del updated_data['id']
            users[data['id']].update(updated_data)
            response.data = json.dumps(users[data['id']])
        else:
            logger.debug('User is new, will create it.')
            # a new user is created
            # data['id'] can't be modified
            new_id = 1 if len(users.keys()) == 0 else max(users.keys()) + 1
            data['id'] = new_id
            users[new_id] = data
            response.data = json.dumps(data)

        return response

    logger.info('Flask app initialized.')

    # Code snippet here represents the current initialization logic
    logger.info('Initializing agent.')
    agent = Agent()
    agent.registerFlaskApp(app)

    # End initialization logic for Python Agent
    logger.info('Agent initialized.')

    logger.info('Server initialized')
    FlaskServer(app)

    logger.info('Running test calls.')
    with app.test_client():
        try:
            body = json.dumps({'id': 1, 'name': 'Jane Doe'})
            logger.info('Making PUT call to /')
            r1 = app.test_client().put('http://localhost:5000/',
                                        data=body,
                                        content_type='application/json')
            logger.info('Reading PUT / response')
            user_data = json.loads(r1.data)
            logger.debug(user_data)
            assert user_data['id'] == 1 and user_data['name'] == 'Jane Doe'

            body = json.dumps({'id': 1, 'name': 'John Doe'})
            logger.info('Making PUT call to /')
            logger.info(body)
            r2 = app.test_client().put('http://localhost:5000/',
                                        data=body,
                                        content_type='application/json')
            logger.info('Reading PUT / response')
            user_data = json.loads(r2.data)
            logger.debug(user_data)
            assert user_data['id'] == 1 and user_data['name'] == 'John Doe'

            body = json.dumps({'name': 'Jana Doe'})
            logger.info('Making PUT call to /')
            logger.info(body)
            r2 = app.test_client().put('http://localhost:5000/',
                                        data=body,
                                        content_type='application/json')
            logger.info('Reading PUT / response')
            user_data = json.loads(r2.data)
            logger.debug(user_data)
            assert user_data['id'] == 2 and user_data['name'] == 'Jana Doe'
        except:
            logger.error('Failed to initialize flask instrumentation wrapper: exception=%s, stacktrace=%s',
                         sys.exc_info()[0],
                         traceback.format_exc())
            raise sys.exc_info()[0]
