import sys
import os.path
import logging
import traceback

from agent.init import AgentInit
from config.logger import get_logger
from config.AgentConfig import AgentConfig

logger = get_logger(__name__)

class Agent:
  def __init__(self):
    logger.debug('Initializing Agent.');
    try:
      self.config = AgentConfig()
      self._init = AgentInit(self)
    except:
      logger.error('Failed to initialize Agent: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())

  def registerFlaskApp(self, app):
    logger.debug('Calling Agent.registerFlaskApp.')
    try:
      self._init.flaskInit(app)
      self._init.dumpConfig()
    except:
      logger.error('Failed to initialize flask instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())

  def registerServerGrpc(self):
    logger.debug('Calling Agent.registerServerGrpc().')
    try:
      self._init.grpcServerInit()
      self._init.dumpConfig()
    except:
      logger.error('Failed to initialize grpc instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())

  def registerClientGrpc(self):
    logger.debug('Calling Agent.registerClientGrpc().')
    try:
      self._init.grpcClientInit()
      self._init.dumpConfig()
    except:
      logger.error('Failed to initialize grpc instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())

  def registerMySQL(self):
    logger.debug('Calling Agent.registerMySQL().')
    try:
      self._init.mySQLInit()
      self._init.dumpConfig()
    except:
      logger.error('Failed to initialize mysql instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())

  def registerPostgreSQL(self):
    logger.debug('Calling Agent.registerPostgreSQL().')
    try:
      self._init.postgreSQLInit()
      self._init.dumpConfig()
    except:
      logger.error('Failed to initialize postgresql instrumentation wrapper: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())

  def globalInit(self):
    logger.debug('Calling Agent.globalInit().')
    try:
      self._init.globalInit()
    except:
      logger.error('Failed to initialize global: exception=%s, stacktrace=%s',
        sys.exc_info()[0],
        traceback.format_exc())

  def getInMemorySpanExport(self):
    return self._init.getInMemorySpanExport()

  def setInMemorySpanExport(self, memory_exporter):
    self._init.setInMemorySpanExport(memory_exporter)
