FLASK_KEY = 'flask'
DJANGO_KEY = 'Django'
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

REGISTERED_LIBRARIES = {}

def get_instrumentation_wrapper(library_key):
    # TODO add flask
    # TODO add try except for import error from nested libraries(or add real import check)
    if DJANGO_KEY == library_key:
        from hypertrace.agent.instrumentation.django import DjangoInstrumentationWrapper
        return DjangoInstrumentationWrapper()
    elif FLASK_KEY == library_key:
        from hypertrace.agent.instrumentation.flask import FlaskInstrumentorWrapper
        return FlaskInstrumentorWrapper()
    elif GRPC_SERVER_KEY == library_key:
        from hypertrace.agent.instrumentation.grpc import GrpcInstrumentorServerWrapper
        return GrpcInstrumentorServerWrapper()
    elif GRPC_CLIENT_KEY == library_key:
        from hypertrace.agent.instrumentation.grpc import GrpcInstrumentorClientWrapper
        return GrpcInstrumentorClientWrapper()
    elif POSTGRESQL_KEY == library_key:
        from hypertrace.agent.instrumentation.postgresql import PostgreSQLInstrumentorWrapper
        return PostgreSQLInstrumentorWrapper()
    elif MYSQL_KEY == library_key:
        from hypertrace.agent.instrumentation.mysql import MySQLInstrumentorWrapper
        return MySQLInstrumentorWrapper()
    elif REQUESTS_KEY == library_key:
        from hypertrace.agent.instrumentation.requests import RequestsInstrumentorWrapper
        return RequestsInstrumentorWrapper()
    elif AIOHTTP_CLIENT_KEY == library_key:
        from hypertrace.agent.instrumentation.aiohttp import AioHttpClientInstrumentorWrapper
        return AioHttpClientInstrumentorWrapper()
    else:
        pass # TODO error case


