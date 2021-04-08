import sys
import logging
import traceback
import json
import psycopg2
from agent import Agent
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor

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
    agent.registerPostgreSQL()
    agent.globalInit()

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
        logger.info('Making connection to postgresql.')
        cnx = psycopg2.connect( database='hypertrace',
                              host='localhost',
                              port=5432,
                              user='postgres',
                              password='postgres'
                            )
        logger.info('Connect successfully.')
        cursor = cnx.cursor()

        # Insert specific data to update later
        logger.info('Running INSERT statement.')
        insert_sql = "INSERT INTO hypertrace_data (col1, col2) VALUES (321, '123456789')"
        cursor.execute(insert_sql)
        logger.info('Statement ran successfully')

        # Update the data
        logger.info('Running UPDATE statement.')
        update_sql = "UPDATE hypertrace_data SET col1=432, col2 = '0303456' WHERE col1 = 321 AND col2='123456789'"
        cursor.execute(update_sql)
        logger.info('Statement ran successfully')

        # Fetch the data to see if it was updated
        logger.info('Running SELECT statement.')
        select_sql = "SELECT * FROM hypertrace_data WHERE col1 = 432 AND col2= '0303456'"
        cursor.execute(select_sql)
        result = cursor.fetchall()
        assert result[0][0] == 432
        assert result[0][1] == '0303456'
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

        # Confirm there are two spans INSERT -> UPDATE -> SELECT
        logger.debug('len(span_list): ' + str(len(span_list)))
        assert len(span_list) == 3

        logger.debug("span 1: insert")
        logger.debug('attributes: ' + str(span_list[0].attributes))
        flaskSpanAsObject = json.loads(span_list[0].to_json())
        assert flaskSpanAsObject['attributes']['db.system'] == 'postgresql'
        assert flaskSpanAsObject['attributes']['db.name'] == 'hypertrace'
        assert flaskSpanAsObject['attributes']['db.statement'] == insert_sql
        assert flaskSpanAsObject['attributes']['db.user'] == 'postgres'
        assert flaskSpanAsObject['attributes']['net.peer.name'] == 'localhost'
        assert flaskSpanAsObject['attributes']['net.peer.port'] == 5432
        logger.debug("span 1: ok")

        logger.debug("span 2: update")
        logger.debug('attributes: ' + str(span_list[1].attributes))
        flaskSpanAsObject = json.loads(span_list[1].to_json())
        assert flaskSpanAsObject['attributes']['db.system'] == 'postgresql'
        assert flaskSpanAsObject['attributes']['db.name'] == 'hypertrace'
        assert flaskSpanAsObject['attributes']['db.statement'] == update_sql
        assert flaskSpanAsObject['attributes']['db.user'] == 'postgres'
        assert flaskSpanAsObject['attributes']['net.peer.name'] == 'localhost'
        assert flaskSpanAsObject['attributes']['net.peer.port'] == 5432
        logger.debug("span 2: ok")

        logger.debug("span 3: select")
        logger.debug('attributes: ' + str(span_list[2].attributes))
        flaskSpanAsObject = json.loads(span_list[2].to_json())
        assert flaskSpanAsObject['attributes']['db.system'] == 'postgresql'
        assert flaskSpanAsObject['attributes']['db.name'] == 'hypertrace'
        assert flaskSpanAsObject['attributes']['db.statement'] == select_sql
        assert flaskSpanAsObject['attributes']['db.user'] == 'postgres'
        assert flaskSpanAsObject['attributes']['net.peer.name'] == 'localhost'
        assert flaskSpanAsObject['attributes']['net.peer.port'] == 5432
        logger.debug("span 3: ok")

        memoryExporter.clear()
        return 0
    except:
        logger.error('Failed to run postgresql tests: exception=%s, stacktrace=%s',
                     sys.exc_info()[0],
                     traceback.format_exc())
        raise sys.exc_info()[0]
