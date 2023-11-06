import flask
import json
from flask import Flask

from tests import setup_custom_logger
from tests.hypertrace.agent.instrumentation.flask.app import FlaskServer

logger = setup_custom_logger(__name__)

logger.info('Initializing flask app.')
# Create Flask app
app = Flask(__name__)
logger.info('Flask app initialized.')


@app.route("/route1")
def api1():
    logger.info('Serving request for /route1.')
    response = flask.Response(mimetype='application/graphql')
    response.headers['tester3'] = 'tester3'
    response.set_cookie("k1", "SomeValue")
    response.set_cookie("k2", "AnotherValue")
    response.data = str('''{
  "errors": [
    {
      "message": "Name for character with ID 1002 could not be fetched.",
      "locations": [ { "line": 6, "column": 7 } ],
      "path": [ "hero", "heroFriends", 1, "name" ]
    }
  ],
  "data": {
    "hero": {
      "name": "R2-D2",
      "heroFriends": [
        {
          "id": "1000",
          "name": "Luke Skywalker"
        },
        {
          "id": "1002",
          "name": null
        },
        {
          "id": "1003",
          "name": "Leia Organa"
        }
      ]
    }
  }
}''').replace('\n', '')
    return response


server = FlaskServer(app)
server.start()


def test_run(agent, exporter):
    agent.instrument(app)
    with app.test_client():
        logger.info('Making test call to /route1')
        r1 = app.test_client().get(f'http://localhost:{server.port}/route1', headers={'tester1': 'tester1', 'tester2': 'tester2'})
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
        assert flaskSpanAsObject['attributes']['http.target'] == '/route1'
        assert flaskSpanAsObject['attributes']['http.request.header.tester1'] == 'tester1'
        assert flaskSpanAsObject['attributes']['http.request.header.tester2'] == 'tester2'
        assert flaskSpanAsObject['attributes']['http.response.header.content-type'] == 'application/graphql'
        assert 'R2-D2' in flaskSpanAsObject['attributes']['http.response.body']
        assert flaskSpanAsObject['attributes']['http.status_code'] == 200
        assert flaskSpanAsObject['attributes']['http.response.header.tester3'] == 'tester3'
        exporter.clear()
        a1 = json.loads(r1.data.decode('UTF8'))['data']['hero']['name']
        logger.info('Reading /route1 response: ' + str(a1))
        assert a1 == 'R2-D2'
        logger.info('r1 result: ' + str(a1))
        logger.info('Exiting from flask instrumentation test.')
    server.shutdown()
