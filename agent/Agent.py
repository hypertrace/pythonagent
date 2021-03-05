# File: Agent.py
# Author: Nitin Sahai
# Date: 03/04/2021
# Notes
#
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__))))
from init import AgentInit

class Agent:
  def __init__(self):
    print('Initializing Agent.');
    self._init = AgentInit.AgentInit()

  def registerFlaskApp(self, app):
    print('Calling registerFlaskApp.')
    self._init.flaskInit(app)
