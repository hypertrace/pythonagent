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
    return library_key in _INSTRUMENTATION_STATE.keys()


def _mark_as_instrumented(library_key, wrapper_instance):
    _INSTRUMENTATION_STATE[library_key] = wrapper_instance


def get_instrumentation_wrapper(library_key):
    if is_already_instrumented(library_key):
        return None
    try:
        wrapper_instance = None
        if DJANGO_KEY == library_key:
            from hypertrace.agent.instrumentation.django import DjangoInstrumentationWrapper
            wrapper_instance = DjangoInstrumentationWrapper()
        elif FLASK_KEY == library_key:
            from hypertrace.agent.instrumentation.flask import FlaskInstrumentorWrapper
            wrapper_instance = FlaskInstrumentorWrapper()
        elif GRPC_SERVER_KEY == library_key:
            from hypertrace.agent.instrumentation.grpc import GrpcInstrumentorServerWrapper
            wrapper_instance = GrpcInstrumentorServerWrapper()
        elif GRPC_CLIENT_KEY == library_key:
            from hypertrace.agent.instrumentation.grpc import GrpcInstrumentorClientWrapper
            wrapper_instance = GrpcInstrumentorClientWrapper()
        elif POSTGRESQL_KEY == library_key:
            from hypertrace.agent.instrumentation.postgresql import PostgreSQLInstrumentorWrapper
            wrapper_instance =  PostgreSQLInstrumentorWrapper()
        elif MYSQL_KEY == library_key:
            from hypertrace.agent.instrumentation.mysql import MySQLInstrumentorWrapper
            wrapper_instance = MySQLInstrumentorWrapper()
        elif REQUESTS_KEY == library_key:
            from hypertrace.agent.instrumentation.requests import RequestsInstrumentorWrapper
            wrapper_instance = RequestsInstrumentorWrapper()
        elif AIOHTTP_CLIENT_KEY == library_key:
            from hypertrace.agent.instrumentation.aiohttp import AioHttpClientInstrumentorWrapper
            wrapper_instance = AioHttpClientInstrumentorWrapper()
        else:
            return None

        _mark_as_instrumented(library_key, wrapper_instance)
        return wrapper_instance
    except Exception as _err:
        logger.warning("Error while attempting to load instrumentation wrapper for %s", library_key)
        return None


