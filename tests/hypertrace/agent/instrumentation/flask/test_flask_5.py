import flask
from tests import setup_custom_logger
from tests.hypertrace.agent.instrumentation.flask.app import FlaskServer

logger = setup_custom_logger(__name__)


def test_run(agent, exporter):
    logger.info('Initializing flask app.')

    # Used for storing users for this test
    users = {"1": {"name": "John Doe"}, "2": {"name": "Jane Doe"}}

    # Create Flask app
    app = flask.Flask(__name__)

    @app.route('/<user_id>', methods=['DELETE'])
    def api_1(user_id):
        logger.info('Serving request for DELETE /%s', user_id)

        response = flask.Response()
        if user_id in users and users[user_id]:
            del users[user_id]
            response.status_code = 200
        else:
            response.status_code = 404

        return response

    server = FlaskServer(app)
    server.start()

    logger.info('Running test calls.')
    with app.test_client():
        logger.info('Making DELETE call to /1')
        r1 = app.test_client().delete('http://localhost:5000/1')
        logger.info('Reading DELETE /1 response')
        assert r1.status_code == 200

        logger.info('Making DELETE call to /1')
        r2 = app.test_client().delete('http://localhost:5000/1')
        logger.info('Reading DELETE /1 response')
        assert r2.status_code == 404

        logger.info('Making DELETE call to /2')
        r3 = app.test_client().delete('http://localhost:5000/2')
        logger.info('Reading DELETE /2 response')
        assert r3.status_code == 200
        server.shutdown()
