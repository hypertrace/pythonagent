import sys
import os.path
import logging
import traceback
from hypertrace.agent.init import AgentInit
from hypertrace.agent.config import AgentConfig

# main logging modle configuration
def setup_custom_logger(name):
  try:
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('agent.log', mode='a')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger
  except Exception as e:
    logger.error('Failed to customize logger: exception=%s, stacktrace=%s',
      e,
      traceback.format_exc())

# create logger object
logger = setup_custom_logger(__name__)

# The Hypertrace Python Agent class
class Agent:
  def __init__(self):
    logger.debug('Initializing Agent.');
    try:
      self._config = AgentConfig()
      self._init = AgentInit(self)
    except Exception as e:
      logger.error('Failed to initialize Agent: exception=%s, stacktrace=%s',
        e,
        traceback.format_exc())

  def registerFlaskApp(self, app, useS3=False):
    logger.debug('Calling Agent.registerFlaskApp.')
    try:
      self._init.flaskInit(app, useS3)
      self._init.dumpConfig()
    except Exception as e:
      logger.error('Failed to initialize flask instrumentation wrapper: exception=%s, stacktrace=%s',
        e,
        traceback.format_exc())

  def registerServerGrpc(self):
    logger.debug('Calling Agent.registerServerGrpc().')
    try:
      self._init.grpcServerInit()
      self._init.dumpConfig()
    except Exception as e:
      logger.error('Failed to initialize grpc instrumentation wrapper: exception=%s, stacktrace=%s',
        e,
        traceback.format_exc())

  def registerClientGrpc(self):
    logger.debug('Calling Agent.registerClientGrpc().')
    try:
      self._init.grpcClientInit()
      self._init.dumpConfig()
    except Exception as e:
      logger.error('Failed to initialize grpc instrumentation wrapper: exception=%s, stacktrace=%s',
        e,
        traceback.format_exc())

  def registerMySQL(self):
    logger.debug('Calling Agent.registerMySQL().')
    try:
      self._init.mySQLInit()
      self._init.dumpConfig()
    except Exception as e:
      logger.error('Failed to initialize mysql instrumentation wrapper: exception=%s, stacktrace=%s',
        e,
        traceback.format_exc())

  def registerPostgreSQL(self):
    logger.debug('Calling Agent.registerPostgreSQL().')
    try:
      self._init.postgreSQLInit()
      self._init.dumpConfig()
    except Exception as e:
      logger.error('Failed to initialize postgresql instrumentation wrapper: exception=%s, stacktrace=%s',
        e,
        traceback.format_exc())

  def registerRequests(self, useB3=False):
    logger.debug('Calling Agent.registerRequests()')
    try:
      self._init.requestsInit(useB3)
      self._init.dumpConfig()
    except Exception as e:
      logger.error('Failed to initialize requests instrumentation wrapper: exception=%s, stacktrace=%s',
        e,
        traceback.format_exc())

  def registerAioHttpClient(self, useB3=False):
    logger.debug('Calling Agent.registerAioHttpClient().')
    try:
      self._init.aioHttpClientInit(useB3)
      self._init.dumpConfig()
    except Exception as e:
      logger.error('Failed to initialize aiohttp-client instrumentation wrapper: exception=%s, stacktrace=%s',
        e,
        traceback.format_exc())

  def setProcessor(self, processor):
    logger.debug('Entering Agent.setProcessor().')
    return self._init.setProcessor(processor)
