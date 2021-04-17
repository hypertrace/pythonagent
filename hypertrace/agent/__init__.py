'''Main entry point for Hypertrace agent module.'''
import sys
import os.path
import logging
import traceback
from hypertrace.agent.init import AgentInit
from hypertrace.agent.config import AgentConfig
from hypertrace.agent import constants

# main logging modle configuration


def setup_custom_logger(name):
    '''Agent logger configuration'''
    try:
        formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        handler = logging.FileHandler('agent.log', mode='a')
        handler.setFormatter(formatter)
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)
        logger_ = logging.getLogger(name)
        logger_.setLevel(logging.INFO)
        logger_.addHandler(handler)
        logger_.addHandler(screen_handler)
        return logger_
    except Exception as err: # pylint: disable=W0703
        print('Failed to customize logger: exception=%s, stacktrace=%s',
              err,
              traceback.format_exc())


# create logger object
logger = setup_custom_logger(__name__) # pylint: disable=C0103

# The Hypertrace Python Agent class
class Agent:
    '''Top-level entry point for Hypertrace agent.'''

    def __init__(self):
        '''Constructor'''
        logger.debug('Initializing Agent.')
        if not self.is_enabled():
            return
        try:
            self._config = AgentConfig()
            self._init = AgentInit(self)
        except Exception as err: # pylint: disable=W0703
            logger.error('Failed to initialize Agent: exception=%s, stacktrace=%s',
                         err,
                         traceback.format_exc())

    def register_flask_app(self, app, use_b3=False):
        '''Register the flask instrumentation module wrapper'''
        logger.debug('Calling Agent.register_flask_app.')
        if not self.is_enabled():
            return
        try:
            self._init.flask_init(app, use_b3)
            self._init.dump_config()
        except Exception as err: # pylint: disable=W0703
            logger.error(constants.EXCEPTION_MESSAGE,
                         'flask',
                         err,
                         traceback.format_exc())

    def register_server_grpc(self):
        '''Register the grpc:server instrumentation module wrapper'''
        logger.debug('Calling Agent.register_server_grpc().')
        if not self.is_enabled():
            return
        try:
            self._init.grpc_server_init()
            self._init.dump_config()
        except Exception as err: # pylint: disable=W0703
            logger.error(constants.EXCEPTION_MESSAGE,
                         'grpc:server',
                         err,
                         traceback.format_exc())

    def register_client_grpc(self):
        '''Register the grpc:client instrumentation module wrapper'''
        logger.debug('Calling Agent.register_client_grpc().')
        if not self.is_enabled():
            return
        try:
            self._init.grpc_client_init()
            self._init.dump_config()
        except Exception as err: # pylint: disable=W0703
            logger.error(constants.EXCEPTION_MESSAGE,
                         'grpc:client',
                         err,
                         traceback.format_exc())

    def register_mysql(self):
        '''Register the mysql instrumentation module wrapper'''
        logger.debug('Calling Agent.register_mysql().')
        if not self.is_enabled():
            return
        try:
            self._init.mysql_init()
            self._init.dump_config()
        except Exception as err: # pylint: disable=W0703
            logger.error(constants.EXCEPTION_MESSAGE,
                         'flask',
                         err,
                         traceback.format_exc())

    def register_postgresql(self):
        '''Register the postgresql instrumentation module wrapper'''
        logger.debug('Calling Agent.register_postgresql().')
        if not self.is_enabled():
            return
        try:
            self._init.postgresql_init()
            self._init.dump_config()
        except Exception as err: # pylint: disable=W0703
            logger.error(constants.EXCEPTION_MESSAGE,
                         'flask',
                         err,
                         traceback.format_exc())

    def register_requests(self, use_b3=False):
        '''Register the requests instrumentation module wrapper'''
        logger.debug('Calling Agent.register_requests()')
        if not self.is_enabled():
            return
        try:
            self._init.requests_init(use_b3)
            self._init.dump_config()
        except Exception as err: # pylint: disable=W0703
            logger.error(constants.EXCEPTION_MESSAGE,
                         'flask',
                         err,
                         traceback.format_exc())

    def register_aiohttp_client(self, use_b3=False):
        '''Register the aiohttp-client instrumentation module wrapper'''
        logger.debug('Calling Agent.register_aiohttp_client().')
        if not self.is_enabled():
            return
        try:
            self._init.aiohttp_client_init(use_b3)
            self._init.dump_config()
        except Exception as err: # pylint: disable=W0703
            logger.error(constants.EXCEPTION_MESSAGE,
                         'flask',
                         err,
                         traceback.format_exc())

    def register_processor(self, processor): # pylint: disable=R1710
        '''Add additional span exporters + processors'''
        logger.debug('Entering Agent.register_processor().')
        if not self.is_enabled():
            return None
        if self.is_enabled():
            return self._init.register_processor(processor)

    def get_config(self):
        '''Return configuration object'''
        return self._config

    def is_enabled(self): # pylint: disable=R0201
        '''Is agent enabled?'''
        if 'HT_ENABLED' in os.environ:
            if os.environ['HT_ENABLED'] == 'false':
                logger.debug("HT_ENABLED is disabled.")
                return False
        return True
