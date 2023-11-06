import flask
import json
from flask import Flask

# Run the flask web server in a separate thread
from tests import setup_custom_logger, find_free_port

# @pytest.mark.serial
from tests.hypertrace.agent.instrumentation.flask.app import FlaskServer

def test_run(agent, exporter):
    logger = setup_custom_logger(__name__)
    logger.info('Initializing flask app.')
    # Create Flask app
    app = Flask(__name__)

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
        json_data = {"message": "Hello [('mysql.infoschema', 'localhost')]"}
        response.data = json.dumps(json_data)
        return response

    logger.info('Flask app initialized.')

    #
    # Code snippet here represents the current initialization logic
    #
    logger.info('Initializing agent.')
    agent.instrument(app)
    logger.info('Agent initialized.')

    server = FlaskServer(app)
    server.start()

    logger.info('Running test calls.')
    with app.test_client() as c:
        logger.info('Making test call to /route1')
        r1 = app.test_client().get(f'http://localhost:{server.port}/route1?foo=bar',
                                   headers={'tester1': 'tester1', 'tester2': 'tester2'})
        # Get all of the in memory spans that were recorded for this iteration
        span_list = exporter.get_finished_spans()
        # Confirm something was returned.
        assert span_list
        # Confirm there are three spans
        logger.debug('len(span_list): ' + str(len(span_list)))
        assert len(span_list) == 1
        logger.debug('span_list: ' + str(span_list[0].attributes))
        flaskSpanAsObject = json.loads(span_list[0].to_json())
        # Check that the expected results are in the flask extended span attributes
        assert flaskSpanAsObject['attributes']['http.method'] == 'GET'
        assert flaskSpanAsObject['attributes']['http.target'] == '/route1?foo=bar'
        assert flaskSpanAsObject['attributes']['http.request.header.tester1'] == 'tester1'
        assert flaskSpanAsObject['attributes']['http.request.header.tester2'] == 'tester2'
        assert flaskSpanAsObject['attributes']['http.response.header.content-type'] == 'application/json'
        assert flaskSpanAsObject['attributes']['http.response.body'] == '{ "a": "a", "xyz": "xyz" }'
        assert flaskSpanAsObject['attributes']['http.status_code'] == 200
        assert flaskSpanAsObject['attributes']['http.response.header.tester3'] == 'tester3'
        exporter.clear()
        logger.info('Making test call to /route2')
        r2 = app.test_client().get('http://localhost:5000/route2',
                                   headers={'tester1': 'tester1', 'tester2': 'tester2'})
        # Confirm something was returned.
        span_list = exporter.get_finished_spans()
        assert span_list
        # Confirm there are three spans
        logger.debug('len(span_list): ' + str(len(span_list)))
        assert len(span_list) == 1
        logger.debug('span_list: ' + str(span_list[0].attributes))
        flaskSpanAsObject = json.loads(span_list[0].to_json())
        # Check that the expected results are in the flask extended span attributes
        assert flaskSpanAsObject['attributes']['http.method'] == 'GET'
        assert flaskSpanAsObject['attributes']['http.target'] == '/route2'
        assert flaskSpanAsObject['attributes']['http.request.header.tester1'] == 'tester1'
        assert flaskSpanAsObject['attributes']['http.request.header.tester2'] == 'tester2'
        assert flaskSpanAsObject['attributes']['http.response.header.content-type'] == 'application/json'
        assert flaskSpanAsObject['attributes'][
                   'http.response.body'] == '{"message": "Hello [(\'mysql.infoschema\', \'localhost\')]"}'
        assert flaskSpanAsObject['attributes']['http.status_code'] == 200
        assert flaskSpanAsObject['attributes']['http.response.header.tester3'] == 'tester3'
        exporter.clear()
        logger.info('Reading /route1 response.')
        a1 = r1.get_json()['a']
        logger.info('Reading /route2 response.')
        a2 = r2.get_json()['message']
        assert a1 == 'a'
        assert a2 == 'Hello [(\'mysql.infoschema\', \'localhost\')]'
        logger.info('r1 result: ' + str(a1))
        logger.info('r2 result: ' + str(a2))
        logger.info('Exiting from flask instrumentation test.')

    server.shutdown()
