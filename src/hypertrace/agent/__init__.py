'''Main entry point for Hypertrace agent module.'''
import os
import os.path
import sys
import threading
import logging
import traceback
from contextlib import contextmanager

import flask

import opentelemetry.trace as ot

from hypertrace.agent.init import AgentInit
from hypertrace.agent.config import AgentConfig
from hypertrace.agent import constants


# main logging module configuration


def setup_custom_logger(name: str) -> logging.Logger:
    '''Agent logger configuration'''
    try:
        formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)
        log_level = logging.INFO
        logger_ = logging.getLogger(name)
        if 'HT_LOG_LEVEL' in os.environ:
            ht_log_level = os.environ['HT_LOG_LEVEL']
            if ht_log_level is None or ht_log_level == '':
                log_level = logging.INFO
            if ht_log_level == 'INFO':
                log_level = logging.INFO
            if ht_log_level == 'DEBUG':
                log_level = logging.DEBUG
            if ht_log_level == 'ERROR':
                log_level = logging.ERROR
            if ht_log_level == 'WARNING':
                log_level = logging.WARNING
            if ht_log_level == 'CRITICAL':
                log_level = logging.CRITICAL
            if ht_log_level == 'NOTSET':
                log_level = logging.NOTSET
        logger_.setLevel(log_level)
        logger_.addHandler(screen_handler)
        return logger_
    except Exception as err:  # pylint: disable=W0703
        print('Failed to customize logger: exception=%s, stacktrace=%s',
              err,
              traceback.format_exc())
        return None


# create logger object
logger = setup_custom_logger(__name__)  # pylint: disable=C0103

# The Hypertrace Python Agent class


class Agent:
    '''Top-level entry point for Hypertrace agent.'''
    _instance = None
    _singleton_lock = threading.Lock()

    def __new__(cls):
        '''constructor'''
        if cls._instance is None:
            with cls._singleton_lock:
                logger.debug('Creating Agent')
                cls._instance = super(Agent, cls).__new__(cls)
                cls._instance._initialized = False
        else:
            logger.debug('Using existing Agent.')
        return cls._instance

    def __init__(self):
        '''Initializer'''
        if not self._initialized: # pylint: disable=E0203:
            logger.debug('Initializing Agent.')
            if not self.is_enabled():
                return
            try:
                self._config = AgentConfig()
                self._init = AgentInit(self._config)
                self._initialized = True
            except Exception as err:  # pylint: disable=W0703
                logger.error('Failed to initialize Agent: exception=%s, stacktrace=%s',
                             err,
                             traceback.format_exc())

    @contextmanager
    def edit_config(self):
        """Used by end users to modify the config"""
        try:
            # need to explicitly set this as None when modifying the config via code
            # to regenerate Trace Provider with new options
            ot._TRACER_PROVIDER = None  # pylint:disable=W0212
            agent_config = self._config.agent_config
            yield agent_config
            self._config.agent_config = agent_config
        finally:
            self._init.apply_config(self._config)

    def register_flask_app(self, app: flask.Flask = None) -> None:
        '''Register the flask instrumentation module wrapper'''
        logger.debug('Calling Agent.register_flask_app.')
        if not self.is_enabled():
            return
        try:
            self._init.init_instrumentation_flask(app)
            self._init.dump_config()
        except Exception as err:  # pylint: disable=W0703
            logger.error(constants.EXCEPTION_MESSAGE,
                         'flask',
                         err,
                         traceback.format_exc())

    def register_grpc_server(self) -> None:
        '''Register the grpc:server instrumentation module wrapper'''
        logger.debug('Calling Agent.register_server_grpc().')
        if not self.is_enabled():
            return
        try:
            self._init.init_instrumentation_grpc_server()
            self._init.dump_config()
        except Exception as err:  # pylint: disable=W0703
            logger.error(constants.EXCEPTION_MESSAGE,
                         'grpc:server',
                         err,
                         traceback.format_exc())

    def register_grpc_client(self) -> None:
        '''Register the grpc:client instrumentation module wrapper'''
        logger.debug('Calling Agent.register_client_grpc().')
        if not self.is_enabled():
            return
        try:
            self._init.init_instrumentation_grpc_client()
            self._init.dump_config()
        except Exception as err:  # pylint: disable=W0703
            logger.error(constants.EXCEPTION_MESSAGE,
                         'grpc:client',
                         err,
                         traceback.format_exc())

    def register_mysql(self) -> None:
        '''Register the mysql instrumentation module wrapper'''
        logger.debug('Calling Agent.register_mysql().')
        if not self.is_enabled():
            return
        try:
            self._init.init_instrumentation_mysql()
            self._init.dump_config()
        except Exception as err:  # pylint: disable=W0703
            logger.error(constants.EXCEPTION_MESSAGE,
                         'mysql',
                         err,
                         traceback.format_exc())

    def register_postgresql(self) -> None:
        '''Register the postgresql instrumentation module wrapper'''
        logger.debug('Calling Agent.register_postgresql().')
        if not self.is_enabled():
            return
        try:
            self._init.init_instrumentation_postgresql()
            self._init.dump_config()
        except Exception as err:  # pylint: disable=W0703
            logger.error(constants.EXCEPTION_MESSAGE,
                         'postgresql',
                         err,
                         traceback.format_exc())

    def register_requests(self) -> None:
        '''Register the requests instrumentation module wrapper'''
        logger.debug('Calling Agent.register_requests()')
        if not self.is_enabled():
            return
        try:
            self._init.init_instrumentation_requests()
            self._init.dump_config()
        except Exception as err:  # pylint: disable=W0703
            logger.error(constants.EXCEPTION_MESSAGE,
                         'requests',
                         err,
                         traceback.format_exc())

    def register_aiohttp_client(self) -> None:
        '''Register the aiohttp-client instrumentation module wrapper'''
        logger.debug('Calling Agent.register_aiohttp_client().')
        if not self.is_enabled():
            return
        try:
            self._init.aiohttp_client_init()
            self._init.dump_config()
        except Exception as err:  # pylint: disable=W0703
            logger.error(constants.EXCEPTION_MESSAGE,
                         'aiohttp_client',
                         err,
                         traceback.format_exc())

    def register_processor(self, processor) -> None:  # pylint: disable=R1710
        '''Add additional span exporters + processors'''
        logger.debug('Entering Agent.register_processor().')
        if not self.is_enabled():
            return None
        if self.is_enabled():
            return self._init.register_processor(processor)

    def is_enabled(self) -> bool:  # pylint: disable=R0201
        '''Is agent enabled?'''
        if 'HT_ENABLED' in os.environ:
            if os.environ['HT_ENABLED'] == 'false':
                logger.debug("HT_ENABLED is disabled.")
                return False
        return True
