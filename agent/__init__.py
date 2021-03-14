import sys
import os.path
import logging
from agent.init import AgentInit

logger = logging.getLogger(__name__)

class Agent:
  def __init__(self):
    logging.basicConfig(filename='agent.log', level=logging.DEBUG)
    logger.debug('Initializing Agent.');
    self._init = AgentInit()

  def registerFlaskApp(self, app):
    logger.debug('Calling Agent.registerFlaskApp.')
    self._init.flaskInit(app)
    self._init.dumpConfig()

  def registerGrpc(self):
    logger.debug('Calling Agent.registerGrpc().')
    self._init.grpcInit()
    self._init.dumpConfig()

  def globalInit(self):
    logger.debug('Calling Agent.globalInit().')
    self._init.globalInit()
