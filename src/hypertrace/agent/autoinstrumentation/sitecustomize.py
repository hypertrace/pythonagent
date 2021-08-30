'''Enable instrumentationon all supported modules.''' # pylint: disable=R0401
import logging
from hypertrace.agent import Agent
from hypertrace.env_var_settings import get_env_value

DEFAULTS = [
  'flask',
  'mysql',
  'postgresql',
  'grpc:server',
  'grpc:client',
  'requests',
  'aiohttp-client'
]

# Initialize logger
logger = logging.getLogger(__name__)  # pylint: disable=C0103

MODULES = ''
instrumented_modules = get_env_value('INSTRUMENTED_MODULES')
if instrumented_modules:
    logger.debug("[env] Loaded INSTRUMENTED_MODULES from env")
    MODULES = instrumented_modules
    if len(MODULES) > 0:
        MODULES = MODULES.replace(' ', '')

if len(MODULES) > 0:
    modules_array = MODULES.split(',')
else:
    modules_array = DEFAULTS

# Create Hypertrace agent
agent = Agent()

# Initialize desired instrumentation wrappers
for mod in modules_array:
    if mod is None or len(mod) == 0:
        continue

    if mod == 'flask':
        agent.register_flask_app()
    elif mod == 'grpc:server':
        agent.register_grpc_server()
    elif mod == 'grpc:client':
        agent.register_grpc_client()
    elif mod == 'mysql':
        agent.register_mysql()
    elif mod == 'postgresql':
        agent.register_postgresql()
    elif mod == 'requests':
        agent.register_requests()
    elif mod == 'aiohttp-client':
        agent.register_aiohttp_client()
    else:
        logger.error('Unknown module name: %s', mod)
