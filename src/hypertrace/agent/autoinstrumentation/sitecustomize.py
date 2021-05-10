'''Enable instrumentationon all supported modules.''' # pylint: disable=R0401
import os
import logging
from hypertrace.agent import Agent

DEFAULTS = [
    'flask',
    'mysql',
    'postgresql',
    'grpc:server',
    'grpc:client',
    'requests',
    'aiohttp'
]

# Initialize logger
logger = logging.getLogger(__name__)  # pylint: disable=C0103

MODULES = ''
if 'HT_INSTRUMENTED_MODULES' in os.environ:
    logger.debug("[env] Loaded HT_INSTRUMENTED_MODULES from env")
    MODULES = os.environ['HT_INSTRUMENTED_MODULES']

modules_array = MODULES.split(',')

if len(modules_array) == 1 and modules_array[0] == '':
    modules_array = DEFAULTS

agent = Agent()

for mod in modules_array:
    if mod is None or len(mod) == 0:
        continue

    if mod == 'flask':
        agent.register_flask_app()
    if mod == 'grpc:server':
        agent.register_grpc_server()
    if mod == 'grpc:client':
        agent.register_grpc_client()
    if mod == 'mysql':
        agent.register_mysql()
    if mod == 'postgresql':
        agent.register_postgresql()
    if mod == 'requests':
        agent.register_requests()
    if mod == 'aiohttp-client':
        agent.register_aiohttp_client()
