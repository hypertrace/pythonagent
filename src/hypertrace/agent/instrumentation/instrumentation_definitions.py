'''this module acts as a driver for instrumentation definitions + application'''
import logging

FLASK_KEY = 'flask'
DJANGO_KEY = 'django'
GRPC_SERVER_KEY = 'grpc:server'
GRPC_CLIENT_KEY = 'grpc:client'
POSTGRESQL_KEY = 'postgresql'
MYSQL_KEY = 'mysql'
REQUESTS_KEY = 'requests'
AIOHTTP_CLIENT_KEY = 'aiohttp:client'

SUPPORTED_LIBRARIES = [
    FLASK_KEY, DJANGO_KEY,
    GRPC_SERVER_KEY, GRPC_CLIENT_KEY,
    POSTGRESQL_KEY, MYSQL_KEY,
    REQUESTS_KEY, AIOHTTP_CLIENT_KEY
]

# map of library_key => instrumentation wrapper instance
_INSTRUMENTATION_STATE = {}

logger = logging.getLogger(__name__)


def is_already_instrumented(library_key):
    """check if an instrumentation wrapper is already registered"""
    return library_key in _INSTRUMENTATION_STATE.keys()


def _mark_as_instrumented(library_key, wrapper_instance):
    """mark an instrumentation wrapper as registered"""
    _INSTRUMENTATION_STATE[library_key] = wrapper_instance


def get_instrumentation_wrapper(library_key):
    """load an initialize an instrumentation wrapper"""
    if is_already_instrumented(library_key):
        return None
    try:
        wrapper_instance = None
        if DJANGO_KEY == library_key:
            from hypertrace.agent.instrumentation.django import DjangoInstrumentationWrapper  #pylint:disable=C0415
            wrapper_instance = DjangoInstrumentationWrapper()
        elif FLASK_KEY == library_key:
            from hypertrace.agent.instrumentation.flask import FlaskInstrumentorWrapper #pylint:disable=C0415
            wrapper_instance = FlaskInstrumentorWrapper()
        elif GRPC_SERVER_KEY == library_key:
            from hypertrace.agent.instrumentation.grpc import GrpcInstrumentorServerWrapper #pylint:disable=C0415
            wrapper_instance = GrpcInstrumentorServerWrapper()
        elif GRPC_CLIENT_KEY == library_key:
            from hypertrace.agent.instrumentation.grpc import GrpcInstrumentorClientWrapper #pylint:disable=C0415
            wrapper_instance = GrpcInstrumentorClientWrapper()
        elif POSTGRESQL_KEY == library_key:
            from hypertrace.agent.instrumentation.postgresql import PostgreSQLInstrumentorWrapper #pylint:disable=C0415
            wrapper_instance =  PostgreSQLInstrumentorWrapper()
        elif MYSQL_KEY == library_key:
            from hypertrace.agent.instrumentation.mysql import MySQLInstrumentorWrapper #pylint:disable=C0415
            wrapper_instance = MySQLInstrumentorWrapper()
        elif REQUESTS_KEY == library_key:
            from hypertrace.agent.instrumentation.requests import RequestsInstrumentorWrapper #pylint:disable=C0415
            wrapper_instance = RequestsInstrumentorWrapper()
        elif AIOHTTP_CLIENT_KEY == library_key:
            from hypertrace.agent.instrumentation.aiohttp import AioHttpClientInstrumentorWrapper #pylint:disable=C0415
            wrapper_instance = AioHttpClientInstrumentorWrapper()
        else:
            return None

        _mark_as_instrumented(library_key, wrapper_instance)
        return wrapper_instance
    except Exception as _err: # pylint:disable=W0703
        logger.debug("Error while attempting to load instrumentation wrapper for %s", library_key)
        return None
