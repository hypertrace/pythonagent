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
    agent.registerMySQL()

    # End initialization logic for Python Agent
    logger.info('Agent initialized.')

    # Setup In-Memory Span Exporter
    logger.info('Agent initialized.')
    logger.info('Adding in-memory span exporter.')
    memoryExporter = InMemorySpanExporter()
    simpleExportSpanProcessor = SimpleSpanProcessor(memoryExporter)
    agent.setProcessor(simpleExportSpanProcessor)
    logger.info('Added in-memoy span exporter')

    try:
        logger.info('Making connection to mysql.')
        cnx = mysql.connector.connect(database='hypertrace',
                                      username='root',
                                      password='example',
                                      host='localhost',
                                      port=3306)
        # Transaction
        logger.info('Starting transaction.')
        cnx.start_transaction()
        logger.info('Transaction initiated')

        logger.info('Connect successfully.')
        cursor = cnx.cursor()

        # Fetch the data to see if it was created
        logger.info('Running INSERT (1) statement.')
        insert_sql_1 = "INSERT INTO hypertrace_data (col1, col2) VALUES (1, 'trx1')"
        cursor.execute(insert_sql_1)
        logger.info('Statement ran successfully')

        logger.info('Running INSERT (2) statement.')
        insert_sql_2 = "INSERT INTO hypertrace_data (col1, col2) VALUES (1, 'trx2')"
        cursor.execute(insert_sql_2)
        logger.info('Statement ran successfully')

        logger.info("Commit")
        cnx.commit()
        logger.info("Commit success")

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
        assert len(span_list) == 2

        logger.debug("span 1: insert")
        logger.debug('attributes: ' + str(span_list[0].attributes))
        flaskSpanAsObject = json.loads(span_list[0].to_json())
        assert flaskSpanAsObject['attributes']['db.system'] == 'mysql'
        assert flaskSpanAsObject['attributes']['db.name'] == 'hypertrace'
        assert flaskSpanAsObject['attributes']['db.statement'] == insert_sql_1
        assert flaskSpanAsObject['attributes']['db.user'] == 'root'
        assert flaskSpanAsObject['attributes']['net.peer.name'] == 'localhost'
        assert flaskSpanAsObject['attributes']['net.peer.port'] == 3306
        logger.debug("span 1: ok")

        logger.debug("span 2: insert")
        logger.debug('attributes: ' + str(span_list[1].attributes))
        flaskSpanAsObject = json.loads(span_list[1].to_json())
        assert flaskSpanAsObject['attributes']['db.system'] == 'mysql'
        assert flaskSpanAsObject['attributes']['db.name'] == 'hypertrace'
        assert flaskSpanAsObject['attributes']['db.statement'] == insert_sql_2
        assert flaskSpanAsObject['attributes']['db.user'] == 'root'
        assert flaskSpanAsObject['attributes']['net.peer.name'] == 'localhost'
        assert flaskSpanAsObject['attributes']['net.peer.port'] == 3306
        logger.debug("span 2: ok")

        memoryExporter.clear()
        return 0
    except:
        logger.error('Failed to run mysql tests: exception=%s, stacktrace=%s',
                     sys.exc_info()[0],
                     traceback.format_exc())
        raise sys.exc_info()[0]
