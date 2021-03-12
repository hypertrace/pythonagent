import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__))))
from init import AgentInit
import logging

class Agent:
  def __init__(self):
    logging.basicConfig(filename='agent.log', level=logging.DEBUG)
    logging.debug('Initializing Agent.');
    self._init = AgentInit()

  def registerFlaskApp(self, app):
    logging.debug('Calling Agent.registerFlaskApp.')
    self._init.flaskInit(app)
    self._init.dumpConfig()

  def registerGrpc(self):
    logging.debug('Calling Agent.registerGrpc().')
    self._init.grpcInit()
    self._init.dumpConfig()

  def globalInit(self):
    logging.debug('Calling Agent.globalInit().')
    self._init.globalInit()
