'''Hypertrace wrapper around OTel MySQL Instrumentor''' # pylint: disable=R0801
import logging
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
from hypertrace.agent.instrumentation import BaseInstrumentorWrapper


# Initialize logger with local module name
logger = logging.getLogger(__name__) # pylint: disable=C0103

class BotocoreInstrumentationWrapper(BotocoreInstrumentor, BaseInstrumentorWrapper):
    '''Hypertrace wrapper around OTel Botocore Instrumentor class'''
