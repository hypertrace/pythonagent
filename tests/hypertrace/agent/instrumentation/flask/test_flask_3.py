import flask
import json
from flask import request, Flask
from tests import setup_custom_logger
from tests.hypertrace.agent.instrumentation.flask.app import FlaskServer

logger = setup_custom_logger(__name__)

logger.info('Initializing flask app.')
# Create Flask app
app = Flask(__name__)
logger.info('Flask app initialized.')


@app.route('/test/postdata', methods=['POST'])
def post_api():
    data = request.get_json()
    logger.info('Serving request for /test/postdata')
    response = flask.Response(mimetype='application/json')
    response.headers['tester3'] = 'tester3'
    sum1 = data['d1'];
    sum2 = data['d2'];
    response.data = str(sum1 + sum2)
    return response


server = FlaskServer(app)


def test_run(agent, exporter):
    agent.instrument(app)
    with app.test_client() as c:
        logger.info('Making test call to /test/postdata')
        r3 = app.test_client().post('http://localhost:5000/test/postdata',
                                    headers={'tester1': 'tester1', 'tester2': 'tester2'},
                                    data=json.dumps({'d1': 10, 'd2': 20}), content_type='application/json')
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
        assert flaskSpanAsObject['attributes']['http.method'] == 'POST'
        assert flaskSpanAsObject['attributes']['http.target'] == '/test/postdata'
        assert flaskSpanAsObject['attributes']['http.request.body'] == '{"d1": 10, "d2": 20}'
        assert flaskSpanAsObject['attributes']['http.request.header.tester1'] == 'tester1'
        assert flaskSpanAsObject['attributes']['http.request.header.tester2'] == 'tester2'
        assert flaskSpanAsObject['attributes']['http.response.header.content-type'] == 'application/json'
        assert flaskSpanAsObject['attributes']['http.response.body'] == '30'
        assert flaskSpanAsObject['attributes']['http.status_code'] == 200
        assert flaskSpanAsObject['attributes']['http.response.header.tester3'] == 'tester3'
        exporter.clear()
        logger.info('Reading /test/postdata response')
        a3 = r3.status_code
        assert a3 == 200
        logger.info('r3 result: ' + str(a3))
        logger.info('Exiting from flask instrumentation test.')
