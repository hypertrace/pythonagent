import json

import flask
import mysql.connector
from flask import Flask
from tests import setup_custom_logger
from tests.hypertrace.agent.instrumentation.flask.app import FlaskServer

logger = setup_custom_logger(__name__)

def get_connection(exporter):
    conn = mysql.connector.connect(database='hypertrace',
                                   username='hypertrace',
                                   password='hypertrace',
                                   host='localhost',
                                   port=3306)

    cursor = conn.cursor()
    cursor.execute("create table if not exists hypertrace_data (col1 INT NOT NULL,col2 VARCHAR(100) NOT NULL);")
    conn.commit()
    exporter.clear()
    return conn


def test_simple_query(agent, exporter):
    agent.instrument()
    conn = get_connection(exporter)

    exporter.clear()

    cursor = conn.cursor()
    cursor.execute("INSERT INTO hypertrace_data (col1, col2) VALUES (123, 'abcdefghijklmnopqrstuvwxyz')")
    cursor.close()
    conn.close()

    span_list = exporter.get_finished_spans()

    assert span_list
    assert len(span_list) == 1
    span = json.loads(span_list[0].to_json())

    assert span['attributes']['db.system'] == 'mysql'
    assert span['attributes']['db.name'] == 'hypertrace'
    assert span['attributes'][
               'db.statement'] == "INSERT INTO hypertrace_data (col1, col2) VALUES (123, 'abcdefghijklmnopqrstuvwxyz')"
    assert span['attributes']['db.user'] == 'hypertrace'
    assert span['attributes']['net.peer.name'] == 'localhost'
    assert span['attributes']['net.peer.port'] == 3306


def test_mysql_within_application(agent, exporter):
    logger = setup_custom_logger(__name__)

    app = Flask(__name__)
    agent.instrument(app)
    conn = get_connection(exporter)

    @app.route("/dbtest")
    def api():
        cnx = get_connection(exporter)
        cursor = cnx.cursor()
        cursor.execute(
            "INSERT INTO hypertrace_data (col1, col2) VALUES (123, 'abcdefghijklmnopqrstuvwxyz')")
        cursor.execute(
            "INSERT INTO hypertrace_data (col1, col2) VALUES (456, 'abcdefghijklmnopqrstuvwxyz')")
        cursor.close()
        cnx.close()
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

            assert len(span_list) == 3

            flaskSpanAsObject = json.loads(span_list[2].to_json())
            sql1SpanAsObject = json.loads(span_list[1].to_json())
            sql2SpanAsObject = json.loads(span_list[0].to_json())

            assert flaskSpanAsObject['attributes']['http.method'] == 'GET'
            assert flaskSpanAsObject['attributes']['http.target'] == '/dbtest'
            assert flaskSpanAsObject['attributes']['http.response.header.content-type'] == 'application/json'
            assert flaskSpanAsObject['attributes'][
                       'http.response.body'] == '{ "a": "a", "xyz": "xyz" }'
            assert flaskSpanAsObject['attributes']['http.status_code'] == 200

            assert sql1SpanAsObject['attributes']['db.system'] == 'mysql'
            assert sql1SpanAsObject['attributes']['db.name'] == 'hypertrace'
            assert sql1SpanAsObject['attributes']['db.user'] == 'hypertrace'
            assert sql1SpanAsObject['attributes']['net.peer.name'] == 'localhost'
            assert sql1SpanAsObject['attributes']['net.peer.port'] == 3306
            assert sql1SpanAsObject['attributes'][
                       'db.statement'] == "INSERT INTO hypertrace_data (col1, col2) VALUES (456, 'abcdefghijklmnopqrstuvwxyz')"

            assert sql2SpanAsObject['attributes']['db.system'] == 'mysql'
            assert sql2SpanAsObject['attributes']['db.name'] == 'hypertrace'
            assert sql2SpanAsObject['attributes']['db.user'] == 'hypertrace'
            assert sql2SpanAsObject['attributes']['net.peer.name'] == 'localhost'
            assert sql2SpanAsObject['attributes']['net.peer.port'] == 3306
            assert sql2SpanAsObject['attributes'][
                       'db.statement'] == "INSERT INTO hypertrace_data (col1, col2) VALUES (123, 'abcdefghijklmnopqrstuvwxyz')"


def test_multiple_mysql_queries(agent, exporter):
    agent.instrument()
    cnx = get_connection(exporter)
    logger.info('Connect successfully.')
    cursor = cnx.cursor()

    # Insert specific data to fetch later
    logger.info('Running INSERT statement.')
    insert_sql = "INSERT INTO hypertrace_data (col1, col2) VALUES (321, '123456789')"
    cursor.execute(insert_sql)
    logger.info('Statement ran successfully')

    logger.info('Running SELECT statement.')
    select_sql = "SELECT * FROM hypertrace_data WHERE col1 = 321 AND col2= '123456789'"

    cursor.execute(select_sql)
    result = cursor.fetchall()
    assert result[0][0] == 321
    assert result[0][1] == '123456789'
    logger.info('Statement ran successfully')

    logger.info('Closing cursor.')
    cursor.close()
    logger.info('Cursor closed')

    logger.info('Closing connection.')
    cnx.close()

    logger.info('Connection closed.')
    # Get all of the in memory spans that were recorded for this iteration
    span_list = exporter.get_finished_spans()
    assert span_list

    # Confirm there are two spans INSERT -> UPDATE
    logger.debug('len(span_list): ' + str(len(span_list)))
    assert len(span_list) == 2

    logger.debug("span 1: insert")
    logger.debug('attributes: ' + str(span_list[0].attributes))
    flaskSpanAsObject = json.loads(span_list[0].to_json())
    assert flaskSpanAsObject['attributes']['db.system'] == 'mysql'
    assert flaskSpanAsObject['attributes']['db.name'] == 'hypertrace'
    assert flaskSpanAsObject['attributes']['db.statement'] == insert_sql
    assert flaskSpanAsObject['attributes']['db.user'] == 'hypertrace'
    assert flaskSpanAsObject['attributes']['net.peer.name'] == 'localhost'
    assert flaskSpanAsObject['attributes']['net.peer.port'] == 3306

    flaskSpanAsObject = json.loads(span_list[1].to_json())
    assert flaskSpanAsObject['attributes']['db.system'] == 'mysql'
    assert flaskSpanAsObject['attributes']['db.name'] == 'hypertrace'
    assert flaskSpanAsObject['attributes']['db.statement'] == select_sql
    assert flaskSpanAsObject['attributes']['db.user'] == 'hypertrace'
    assert flaskSpanAsObject['attributes']['net.peer.name'] == 'localhost'
    assert flaskSpanAsObject['attributes']['net.peer.port'] == 3306


def test_multiple_mysql_queries_2(agent, exporter):
    agent.instrument()
    logger = setup_custom_logger(__name__)
    cnx = get_connection(exporter)

    cursor = cnx.cursor()

    insert_sql = "INSERT INTO hypertrace_data (col1, col2) VALUES (321, '123456789')"
    cursor.execute(insert_sql)

    update_sql = "UPDATE hypertrace_data SET col1=432, col2 = '0303456' WHERE col1 = 321 AND col2='123456789'"
    cursor.execute(update_sql)
    cursor.fetchall()

    logger.info('Running SELECT statement.')
    select_sql = "SELECT * FROM hypertrace_data WHERE col1 = 432 AND col2= '0303456'"
    cursor.execute(select_sql)
    result = cursor.fetchall()
    assert result[0][0] == 432
    assert result[0][1] == '0303456'

    cursor.close()
    cnx.close()

    span_list = exporter.get_finished_spans()
    assert span_list

    assert len(span_list) == 3
    expected_sql_statements = [insert_sql, update_sql, select_sql]
    for i in range(len(expected_sql_statements)):
        span = json.loads(span_list[i].to_json())
        assert span['attributes']['db.system'] == 'mysql'
        assert span['attributes']['db.name'] == 'hypertrace'
        assert span['attributes']['db.statement'] == expected_sql_statements[i]
        assert span['attributes']['db.user'] == 'hypertrace'
        assert span['attributes']['net.peer.name'] == 'localhost'
        assert span['attributes']['net.peer.port'] == 3306


def test_multiple_queries_3(agent, exporter):
    agent.instrument()
    logger = setup_custom_logger(__name__)

    cnx = mysql.connector.connect(database='hypertrace',
                                  username='hypertrace',
                                  password='hypertrace',
                                  host='localhost',
                                  port=3306)
    cursor = cnx.cursor()

    insert_sql = "INSERT INTO hypertrace_data (col1, col2) VALUES (321, '123456789')"
    cursor.execute(insert_sql)

    delete_sql = "DELETE FROM hypertrace_data WHERE col1 = 321 AND col2='123456789'"
    cursor.execute(delete_sql)
    cursor.fetchall()

    select_sql = "SELECT * FROM hypertrace_data WHERE col1 = 432 AND col2= '0303456'"
    cursor.execute(select_sql)
    result = cursor.fetchall()
    assert result == []

    cursor.close()

    cnx.close()

    span_list = exporter.get_finished_spans()
    assert span_list

    logger.debug('len(span_list): ' + str(len(span_list)))

    expected_sql_statements = [insert_sql, delete_sql, select_sql]
    for i in range(len(expected_sql_statements)):
        span = json.loads(span_list[i].to_json())
        assert span['attributes']['db.system'] == 'mysql'
        assert span['attributes']['db.name'] == 'hypertrace'
        assert span['attributes']['db.statement'] == expected_sql_statements[i]
        assert span['attributes']['db.user'] == 'hypertrace'
        assert span['attributes']['net.peer.name'] == 'localhost'
        assert span['attributes']['net.peer.port'] == 3306


def test_procedure_is_captured(agent, exporter):
    agent.instrument()
    cnx = mysql.connector.connect(database='hypertrace',
                                  username='hypertrace',
                                  password='hypertrace',
                                  host='localhost',
                                  port=3306)

    cursor = cnx.cursor()
    delete_procedure = """DROP PROCEDURE IF EXISTS add_data"""
    cursor.execute(delete_procedure)

    procedure_sql = """CREATE PROCEDURE add_data(IN col1 INT, IN col2 VARCHAR(100))
    BEGIN
      INSERT INTO hypertrace_data (col1, col2) VALUES (col1, col2);
    END"""
    cursor.execute(procedure_sql)

    cursor.callproc('add_data', (123, "456"))

    select_sql = "SELECT * FROM hypertrace_data"
    cursor.execute(select_sql)
    result = cursor.fetchall()
    assert result == [(123, "456")]

    cursor.close()

    cnx.close()


    # Get all of the in memory spans that were recorded for this iteration
    span_list = exporter.get_finished_spans()
    assert span_list

    assert len(span_list) == 4

    expected_sql_statements = [delete_procedure, procedure_sql, "add_data", select_sql]

    for i in range(len(expected_sql_statements)):
        span = json.loads(span_list[i].to_json())
        assert span['attributes']['db.system'] == 'mysql'
        assert span['attributes']['db.name'] == 'hypertrace'
        assert span['attributes']['db.statement'] == expected_sql_statements[i]
        assert span['attributes']['db.user'] == 'hypertrace'
        assert span['attributes']['net.peer.name'] == 'localhost'
        assert span['attributes']['net.peer.port'] == 3306
