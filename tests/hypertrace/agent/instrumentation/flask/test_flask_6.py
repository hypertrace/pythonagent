import flask
from tests import setup_custom_logger
from tests.hypertrace.agent.instrumentation.flask.app import FlaskServer

logger = setup_custom_logger(__name__)


def test_run(agent, exporter):
    logger.info('Initializing flask app.')

    # Create Flask app
    app = flask.Flask(__name__)

    @app.route('/', methods=['OPTIONS'])
    def api_1():
        logger.info('Serving request for OPTIONS /')
        response = flask.Response()
        response.headers['Allow'] = ['OPTIONS']
        return response

    agent.instrument(app)

    server = FlaskServer(app)
    server.start()

    logger.info('Running test calls.')
    with app.test_client():
        logger.info('Making OPTIONS call to /')
        r1 = app.test_client().options(f'http://localhost:{server.port}/')
        assert r1.headers['Allow'] == "['OPTIONS']"
        server.shutdown()