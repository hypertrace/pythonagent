'''Enable instrumentationon all supported modules.''' # pylint: disable=R0401
import logging
from hypertrace.agent import Agent
from hypertrace.env_var_settings import get_env_value

<<<<<<< HEAD
=======
DEFAULTS = [
  'Django',
  'flask',
  'mysql',
  'postgresql',
  'grpc:server',
  'grpc:client',
  'requests',
  'aiohttp-client'
]

>>>>>>> a8f51e49dc6c3b11f9f77dc4300c964f53909d60
# Initialize logger
logger = logging.getLogger(__name__)  # pylint: disable=C0103

skip_modules = get_env_value('SKIP_MODULES')
if skip_modules:
    logger.debug("[env] Loaded SKIP_MODULES from env")
    if len(skip_modules) > 0:
        skip_modules = skip_modules.replace(' ', '')
        skip_modules = skip_modules.split(',')
else:
    skip_modules = []

# Create Hypertrace agent
agent = Agent()
agent.instrument(skip_modules)