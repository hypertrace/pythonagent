import json
import flask
import psycopg2
from flask import Flask

from tests import setup_custom_logger
from tests.hypertrace.agent.instrumentation.flask.app import FlaskServer

logger = setup_custom_logger(__name__)

def get_connection(exporter):
    conn = psycopg2.connect(database='hypertrace',
                            host='localhost',
                            port=5432,
                            user='hypertrace',
                            password='hypertrace')

    cursor = conn.cursor()
    cursor.execute("create table if not exists hypertrace_data (col1 INT NOT NULL,col2 VARCHAR(100) NOT NULL);")
    conn.commit()
    exporter.clear()
    return conn


def test_capture_simple_insert(agent, exporter):
    agent.instrument()
    conn = get_connection(exporter)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO hypertrace_data (col1, col2) VALUES (123, 'abcdefghijklmnopqrstuvwxyz')")
    conn.close()

    spans = exporter.get_finished_spans()
    assert spans

    assert len(spans) == 1
    logger.debug(spans)
    span = json.loads(spans[0].to_json())
    assert span['attributes']['db.system'] == 'postgresql'
    assert span['attributes']['db.name'] == 'hypertrace'
    assert span['attributes'][
               'db.statement'] == "INSERT INTO hypertrace_data (col1, col2) VALUES (123, 'abcdefghijklmnopqrstuvwxyz')"
    assert span['attributes']['db.user'] == 'hypertrace'
    assert span['attributes']['net.peer.name'] == 'localhost'
    assert span['attributes']['net.peer.port'] == 5432
    exporter.clear()


def test_within_application(agent, exporter):
    app = Flask(__name__)
    agent.instrument(app)

    @app.route("/dbtest")
    def api1():
        appCnx = psycopg2.connect(database='hypertrace',
                                  host='localhost',
                                  port=5432,
                                  user='hypertrace',
                                  password='hypertrace'
                                  )
        appCursor = appCnx.cursor()
        appCursor.execute("INSERT INTO hypertrace_data (col1, col2) VALUES (123, 'abcdefghijklmnopqrstuvwxyz')")
        appCursor.execute("INSERT INTO hypertrace_data (col1, col2) VALUES (456, 'abcdefghijklmnopqrstuvwxyz')")
        appCursor.close()
        appCnx.close()
        response = flask.Response(mimetype='application/json')
        response.data = str('{ "a": "a", "xyz": "xyz" }')
        return response

    server = FlaskServer(app)

    logger.info('Running test calls.')
    with app.test_client() as c:
        logger.info('Making test call to /dbtest')
        for x in range(10):  # Run 10 requests
            r1 = app.test_client().get(f'http://localhost:{server.port}/dbtest')
            logger.info('Reading /dbtest response.')
            a1 = r1.get_json()['a']
            assert a1 == 'a'
            # Get all of the in memory spans that were recorded for this iteration
            span_list = exporter.get_finished_spans()
            # Confirm something was returned.
            assert span_list
            # Confirm there are three spans
            logger.debug('len(span_list): ' + str(len(span_list)))
            assert len(span_list) == 3
            logger.debug('span_list: ' + str(span_list[2].attributes))
            logger.debug('span_list: ' + str(span_list[1].attributes))
            logger.debug('span_list: ' + str(span_list[0].attributes))
            # Convert each span to a JSON object
            flaskSpanAsObject = json.loads(span_list[2].to_json())
            sql1SpanAsObject = json.loads(span_list[1].to_json())
            sql2SpanAsObject = json.loads(span_list[0].to_json())

            for key in flaskSpanAsObject:
                logger.debug(key + ' : ' + str(flaskSpanAsObject[key]))
                # Check that the expected results are in the flask extended span attributes
            assert flaskSpanAsObject['attributes']['http.method'] == 'GET'
            assert flaskSpanAsObject['attributes']['http.target'] == '/dbtest'
            assert flaskSpanAsObject['attributes']['http.response.header.content-type'] == 'application/json'
            assert flaskSpanAsObject['attributes']['http.response.body'] == '{ "a": "a", "xyz": "xyz" }'
            assert flaskSpanAsObject['attributes']['http.status_code'] == 200

            for key in sql1SpanAsObject:
                logger.debug(key + ' : ' + str(sql1SpanAsObject[key]))
            assert sql1SpanAsObject['attributes']['db.system'] == 'postgresql'
            assert sql1SpanAsObject['attributes']['db.name'] == 'hypertrace'
            assert sql1SpanAsObject['attributes']['db.user'] == 'hypertrace'
            assert sql1SpanAsObject['attributes']['net.peer.name'] == 'localhost'
            assert sql1SpanAsObject['attributes']['net.peer.port'] == 5432
            assert sql1SpanAsObject['attributes'][
                       'db.statement'] == "INSERT INTO hypertrace_data (col1, col2) VALUES (456, 'abcdefghijklmnopqrstuvwxyz')"
            for key in sql2SpanAsObject:
                logger.debug(key + ' : ' + str(sql2SpanAsObject[key]))
            assert sql2SpanAsObject['attributes']['db.system'] == 'postgresql'
            assert sql2SpanAsObject['attributes']['db.name'] == 'hypertrace'
            assert sql2SpanAsObject['attributes']['db.user'] == 'hypertrace'
            assert sql2SpanAsObject['attributes']['net.peer.name'] == 'localhost'
            assert sql2SpanAsObject['attributes']['net.peer.port'] == 5432
            assert sql2SpanAsObject['attributes'][
                       'db.statement'] == "INSERT INTO hypertrace_data (col1, col2) VALUES (123, 'abcdefghijklmnopqrstuvwxyz')"
            exporter.clear()
            logger.info('r1 result: ' + str(a1))
    logger.info('Exiting from flask + postgresql instrumentation test.')


def test_multiple_queries(agent, exporter):
    logger.info('Making connection to postgresql.')
    agent.instrument()
    cnx = psycopg2.connect(database='hypertrace',
                           host='localhost',
                           port=5432,
                           user='hypertrace',
                           password='hypertrace'
                           )
    cursor = cnx.cursor()

    insert_sql = "INSERT INTO hypertrace_data (col1, col2) VALUES (321, '123456789')"
    cursor.execute(insert_sql)
    select_sql = "SELECT * FROM hypertrace_data WHERE col1 = 321 AND col2= '123456789'"

    cursor.execute(select_sql)
    result = cursor.fetchall()
    assert result[0][0] == 321
    assert result[0][1] == '123456789'

    cursor.close()
    cnx.close()

    span_list = exporter.get_finished_spans()
    assert span_list

    assert len(span_list) == 2

    insert_span = json.loads(span_list[0].to_json())
    assert insert_span['attributes']['db.system'] == 'postgresql'
    assert insert_span['attributes']['db.name'] == 'hypertrace'
    assert insert_span['attributes']['db.statement'] == insert_sql
    assert insert_span['attributes']['db.user'] == 'hypertrace'
    assert insert_span['attributes']['net.peer.name'] == 'localhost'
    assert insert_span['attributes']['net.peer.port'] == 5432

    update_span = json.loads(span_list[1].to_json())
    assert update_span['attributes']['db.system'] == 'postgresql'
    assert update_span['attributes']['db.name'] == 'hypertrace'
    assert update_span['attributes']['db.statement'] == select_sql
    assert update_span['attributes']['db.user'] == 'hypertrace'
    assert update_span['attributes']['net.peer.name'] == 'localhost'
    assert update_span['attributes']['net.peer.port'] == 5432


def test_multiple_queries_2(agent, exporter):
    agent.instrument()
    cnx = psycopg2.connect(database='hypertrace',
                           host='localhost',
                           port=5432,
                           user='hypertrace',
                           password='hypertrace'
                           )
    cursor = cnx.cursor()

    insert_sql = "INSERT INTO hypertrace_data (col1, col2) VALUES (321, '123456789')"
    cursor.execute(insert_sql)

    update_sql = "UPDATE hypertrace_data SET col1=432, col2 = '0303456' WHERE col1 = 321 AND col2='123456789'"
    cursor.execute(update_sql)

    select_sql = "SELECT * FROM hypertrace_data WHERE col1 = 432 AND col2= '0303456'"
    cursor.execute(select_sql)
    result = cursor.fetchall()
    assert result[0][0] == 432
    assert result[0][1] == '0303456'

    cursor.close()
    cnx.close()

    # Get all of the in memory spans that were recorded for this iteration
    span_list = exporter.get_finished_spans()
    assert span_list

    assert len(span_list) == 3
    expected_statements = [insert_sql, update_sql, select_sql]
    for i in range(len(expected_statements)):
        expected_statement = expected_statements[i]
        span = json.loads(span_list[i].to_json())
        assert span['attributes']['db.system'] == 'postgresql'
        assert span['attributes']['db.name'] == 'hypertrace'
        assert span['attributes']['db.statement'] == expected_statement
        assert span['attributes']['db.user'] == 'hypertrace'
        assert span['attributes']['net.peer.name'] == 'localhost'
        assert span['attributes']['net.peer.port'] == 5432
