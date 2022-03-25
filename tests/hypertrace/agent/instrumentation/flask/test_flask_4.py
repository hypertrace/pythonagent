import flask
import json
from tests import setup_custom_logger
from tests.hypertrace.agent.instrumentation.flask.app import FlaskServer

logger = setup_custom_logger(__name__)


def test_run(agent, exporter):
    logger.info('Initializing flask app.')

    # Used for storing users for this test
    users = {}

    # Create Flask app
    app = flask.Flask(__name__)

    @app.route('/', methods=['PUT'])
    def api_1():
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

    agent.instrument(app)
    server = FlaskServer(app)
    server.start()

    with app.test_client():
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
        server.shutdown()