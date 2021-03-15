import sys
import os.path
import logging
import traceback
from agent.init import AgentInit

logger = logging.getLogger(__name__)

class Agent:
  def __init__(self):
    logging.basicConfig(filename='agent.log', level=logging.DEBUG)
    logger.debug('Initializing Agent.');
    try:
      self._init = AgentInit()
    except e:
      logger.error('Failed to initialize Agent.')
      traceback.print_exc()

  def registerFlaskApp(self, app):
    logger.debug('Calling Agent.registerFlaskApp.')
    try:
      self._init.flaskInit(app)
      self._init.dumpConfig()
    except e:
      logger.error('Failed to initialize flask instrumentation wrapper.')
      traceback.print_exc()

  def registerGrpc(self):
    logger.debug('Calling Agent.registerGrpc().')
    try:
      self._init.grpcInit()
      self._init.dumpConfig()
    except e:
      logger.error('Failed to initialize grpc instrumentation wrapper')
      traceback.print_exc()

  def globalInit(self):
    logger.debug('Calling Agent.globalInit().')
    try:
      self._init.globalInit()
    except e:
      logger.error('Failed to initialize global.')
      traceback.print_exc()      
