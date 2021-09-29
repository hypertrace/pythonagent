import sys
import logging
import traceback
import json
import mysql.connector
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
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
        logger.error('Failed to customize logger: exception=%s, stacktrace=%s',
                     sys.exc_info()[0],
                     traceback.format_exc())


def test_run():
    logger = setup_custom_logger(__name__)

    # Code snippet here represents the current initialization logic
    logger.info('Initializing agent.')
    agent = Agent()
    agent.instrument()

    # End initialization logic for Python Agent
    logger.info('Agent initialized.')

    # Setup In-Memory Span Exporter
    logger.info('Agent initialized.')
    logger.info('Adding in-memory span exporter.')
    memoryExporter = InMemorySpanExporter()
    simpleExportSpanProcessor = SimpleSpanProcessor(memoryExporter)
    agent.register_processor(simpleExportSpanProcessor)
    logger.info('Added in-memoy span exporter')

    try:
        logger.info('Making connection to mysql.')
        cnx = mysql.connector.connect(database='hypertrace',
                                      username='root',
                                      password='root',
                                      host='localhost',
                                      port=3306)
        logger.info('Connect successfully.')
        cursor = cnx.cursor()

        # Create procedure
        logger.info('Running CREATE PROCEDURE statement.')
        procedure_sql = """CREATE PROCEDURE add_data(IN col1 INT, IN col2 VARCHAR(100))
BEGIN
  INSERT INTO hypertrace_data (col1, col2) VALUES (col1, col2);
END"""
        cursor.execute(procedure_sql)
        logger.info('Statement ran successfully')

        # Insert a register calling procedure
        logger.info('Running: Exec add_data')
        cursor.callproc('add_data', (123, "456"))
        logger.info('Statement ran successfully')

        # Fetch the data to see if it was created
        logger.info('Running SELECT statement.')
        select_sql = "SELECT * FROM hypertrace_data"
        cursor.execute(select_sql)
        result = cursor.fetchall()
        assert result == [(123, "456")]
        logger.info('Statement ran successfully')

        logger.info('Closing cursor.')
        cursor.close()
        logger.info('Cursor closed')

        logger.info('Closing connection.')
        cnx.close()

        logger.info('Connection closed.')

        # Get all of the in memory spans that were recorded for this iteration
        span_list = memoryExporter.get_finished_spans()
        assert span_list

        # Confirm there are two spans INSERT -> DELETE -> SELECT
        logger.debug('len(span_list): ' + str(len(span_list)))
        assert len(span_list) == 3

        logger.debug("span 1: create procedure")
        logger.debug('attributes: ' + str(span_list[0].attributes))
        flaskSpanAsObject = json.loads(span_list[0].to_json())
        assert flaskSpanAsObject['attributes']['db.system'] == 'mysql'
        assert flaskSpanAsObject['attributes']['db.name'] == 'hypertrace'
        assert flaskSpanAsObject['attributes']['db.statement'] == procedure_sql
        assert flaskSpanAsObject['attributes']['db.user'] == 'root'
        assert flaskSpanAsObject['attributes']['net.peer.name'] == 'localhost'
        assert flaskSpanAsObject['attributes']['net.peer.port'] == 3306
        logger.debug("span 1: ok")

        logger.debug("span 2: select")
        logger.debug('attributes: ' + str(span_list[1].attributes))
        flaskSpanAsObject = json.loads(span_list[1].to_json())
        assert flaskSpanAsObject['attributes']['db.system'] == 'mysql'
        assert flaskSpanAsObject['attributes']['db.name'] == 'hypertrace'
        assert flaskSpanAsObject['attributes']['db.statement'] == "add_data"
        assert flaskSpanAsObject['attributes']['db.user'] == 'root'
        assert flaskSpanAsObject['attributes']['net.peer.name'] == 'localhost'
        assert flaskSpanAsObject['attributes']['net.peer.port'] == 3306
        logger.debug("span 2: ok")

        logger.debug("span 3: select")
        logger.debug('attributes: ' + str(span_list[2].attributes))
        flaskSpanAsObject = json.loads(span_list[2].to_json())
        assert flaskSpanAsObject['attributes']['db.system'] == 'mysql'
        assert flaskSpanAsObject['attributes']['db.name'] == 'hypertrace'
        assert flaskSpanAsObject['attributes']['db.statement'] == select_sql
        assert flaskSpanAsObject['attributes']['db.user'] == 'root'
        assert flaskSpanAsObject['attributes']['net.peer.name'] == 'localhost'
        assert flaskSpanAsObject['attributes']['net.peer.port'] == 3306
        logger.debug("span 3: ok")

        memoryExporter.clear()
        return 0
    except:
        logger.error('Failed to run mysql tests: exception=%s, stacktrace=%s',
                     sys.exc_info()[0],
                     traceback.format_exc())
        raise sys.exc_info()[0]
