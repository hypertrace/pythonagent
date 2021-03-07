import sys
import os.path
import logging

class BaseInstrumentorWrapper:
  def __init__(self):
    logging.debug('Entering BaseInstrumentorWrapper constructor.');
    super().__init__() 
