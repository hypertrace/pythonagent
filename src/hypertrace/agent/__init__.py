'''Main entry point for Hypertrace agent module.'''
import sys
import threading
import traceback
from contextlib import contextmanager

import opentelemetry.trace as ot

from hypertrace.agent.instrumentation.instrumentation_definitions import SUPPORTED_LIBRARIES, \
    get_instrumentation_wrapper
from hypertrace.env_var_settings import get_env_value
from hypertrace.agent.init import AgentInit
from hypertrace.agent.config import AgentConfig
from hypertrace.agent import constants
from hypertrace.agent import custom_logger

# The Hypertrace Python Agent class

logger = custom_logger.get_custom_logger(__name__)

class Agent:
    '''Top-level entry point for Hypertrace agent.'''
    _instance = None
    _singleton_lock = threading.Lock()

    def __new__(cls):
        '''constructor'''
        if cls._instance is None:
            with cls._singleton_lock:
                logger.debug('Creating Agent')
                logger.debug('Python version: %s', sys.version)
                cls._instance = super(Agent, cls).__new__(cls)
                cls._instance._initialized = False
        else:
            logger.debug('Using existing Agent.')
        return cls._instance

    def __init__(self):
        '''Initializer'''
        self._initialized = False
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

    def instrument(self, skip_libraries: []):
        '''used to register applicable instrumentation wrappers'''
        if not self.is_initialized():
            logger.debug('agent is not initialized, not instrumenting')
            return

        for library_key in SUPPORTED_LIBRARIES:
            if library_key in skip_libraries:
                logger.debug('not attempting to instrument %s', library_key)
                continue
            wrapper_instance = get_instrumentation_wrapper(library_key)
            self.register_library(library_key, wrapper_instance)


    def register_library(self, library_name, wrapper_instance) -> bool:
        logger.debug('attempting to register library instrumentation: %s', library_name)
        try:
            self._init.init_library_instrumentation(library_name, wrapper_instance)
            return True
        except Exception as err:  # pylint: disable=W0703
            logger.debug(constants.EXCEPTION_MESSAGE,
                         library_name,
                         err,
                         traceback.format_exc())
            return False

    # def register_flask_app(self, app = None) -> None:
    #     '''Register the flask instrumentation module wrapper'''
    #     logger.debug('Calling Agent.register_flask_app.')
    #     if not self.is_initialized():
    #         return
    #     try:
    #         self._init.init_instrumentation_flask(app)
    #         self._init.dump_config()
    #     except Exception as err:  # pylint: disable=W0703
    #         logger.debug(constants.EXCEPTION_MESSAGE,
    #                      'flask',
    #                      err,
    #                      traceback.format_exc())

    def register_processor(self, processor) -> None:  # pylint: disable=R1710
        '''Add additional span exporters + processors'''
        logger.debug('Entering Agent.register_processor().')
        logger.debug("initialized %s", self.is_initialized())
        if not self.is_initialized():
            return None
        return self._init.register_processor(processor)

    def is_enabled(self) -> bool:  # pylint: disable=R0201
        '''Is agent enabled?'''
        enabled = get_env_value('ENABLED')
        if enabled:
            if enabled.lower() == 'false':
                logger.debug("ENABLED is disabled.")
                return False
        return True

    def is_initialized(self) -> bool:  # pylint: disable=R0201
        '''Is agent initialized - if an agent fails to init we should let the app continue'''
        if not self.is_enabled():
            return False
        if not self._initialized:
            return False
        return True
