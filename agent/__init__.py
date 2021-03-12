import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__))))
from init import AgentInit
import logging

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
