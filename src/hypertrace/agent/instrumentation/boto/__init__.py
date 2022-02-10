'''Hypertrace wrapper around OTel boto Instrumentor''' # pylint: disable=R0801
import logging
from opentelemetry.instrumentation.boto import BotoInstrumentor  # pylint:disable=E0611,E0401
from hypertrace.agent.instrumentation import BaseInstrumentorWrapper


# Initialize logger with local module name
logger = logging.getLogger(__name__) # pylint: disable=C0103

class BotoInstrumentationWrapper(BotoInstrumentor, BaseInstrumentorWrapper):
    '''Hypertrace wrapper around OTel Boto Instrumentor class'''
