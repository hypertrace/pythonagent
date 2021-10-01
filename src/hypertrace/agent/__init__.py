'''Main entry point for Hypertrace agent module.'''
import sys
import threading
import traceback
from contextlib import contextmanager

from deprecated import deprecated
import opentelemetry.trace as ot

from hypertrace.agent.instrumentation.instrumentation_definitions import SUPPORTED_LIBRARIES, \
    get_instrumentation_wrapper, REQUESTS_KEY, GRPC_CLIENT_KEY, DJANGO_KEY, MYSQL_KEY, GRPC_SERVER_KEY, \
    POSTGRESQL_KEY, AIOHTTP_CLIENT_KEY, FLASK_KEY
from hypertrace.env_var_settings import get_env_value
from hypertrace.agent.init import AgentInit
from hypertrace.agent.config import AgentConfig
from hypertrace.agent import constants
from hypertrace.agent import custom_logger
from hypertrace.version import __version__
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
                logger.debug('Hypertrace Agent version: %s', __version__)
                cls._instance = super(Agent, cls).__new__(cls)
                cls._instance._initialized = False
        else:
            logger.debug('Using existing Agent.')
        return cls._instance

    def __init__(self):
        '''Initializer'''
        self._initialized = False
        if not self._initialized:  # pylint: disable=E0203:
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

    def instrument(self, app=None, skip_libraries=None):
        '''used to register applicable instrumentation wrappers'''
        if skip_libraries is None:
            skip_libraries = []
        if not self.is_initialized():
            logger.debug('agent is not initialized, not instrumenting')
            return

        for library_key in SUPPORTED_LIBRARIES:
            if library_key in skip_libraries:
                logger.debug('not attempting to instrument %s', library_key)
                continue

            self._instrument(library_key, app)

    def _instrument(self, library_key, app=None):
        """only used to allow the deprecated register_x library methods to still work"""
        wrapper_instance = get_instrumentation_wrapper(library_key)
        if wrapper_instance is None:
            return

        # Flask is a special case compared to rest of instrumentation
        # using hypertrace-instrument we can replace flask class def before app is initialized
        # however during code based instr we wrap the existing app
        # since replacing class def after app is initialized doesnt have an effect
        # the user has to pass the app in to agent.instrument()
        # we could resolve this edge case by instead having users directly add the middleware
        # ex: app = Flask();
        # app = HypertraceMiddleware(App) => this in turn does agent.instrument()
        # + we have ref to app
        if library_key == FLASK_KEY and app is not None:
            wrapper_instance.with_app(app)

        self.register_library(library_key, wrapper_instance)

    def register_library(self, library_name, wrapper_instance):
        """will configure settings on an instrumentation wrapper + apply"""
        logger.debug('attempting to register library instrumentation: %s', library_name)
        try:
            self._init.init_library_instrumentation(library_name, wrapper_instance)
        except Exception as err:  # pylint: disable=W0703
            logger.debug(constants.EXCEPTION_MESSAGE, library_name, err, traceback.format_exc())

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

    # These methods are deprecated and replaced by a single call to `agent_instance.instrument()`
    AGENT_INSTRUMENT_INSTEAD = "You should use agent.instrument() instead"
    AGENT_INSTRUMENT_VERSION = '0.6.0'

    @deprecated(version=AGENT_INSTRUMENT_VERSION, reason=AGENT_INSTRUMENT_INSTEAD)
    def register_requests(self):
        """just a proxy to support deprecated method for instrumenting requests"""
        self._instrument(REQUESTS_KEY)

    @deprecated(version=AGENT_INSTRUMENT_VERSION, reason=AGENT_INSTRUMENT_INSTEAD)
    def register_grpc_client(self):
        """just a proxy to support deprecated method for instrumenting grpc_client"""
        self._instrument(GRPC_CLIENT_KEY)

    @deprecated(version=AGENT_INSTRUMENT_VERSION, reason=AGENT_INSTRUMENT_INSTEAD)
    def register_django(self):
        """just a proxy to support deprecated method for instrumenting django"""
        self._instrument(DJANGO_KEY)

    @deprecated(version=AGENT_INSTRUMENT_VERSION, reason=AGENT_INSTRUMENT_INSTEAD)
    def register_mysql(self):
        """just a proxy to support deprecated method for instrumenting mysql"""
        self._instrument(MYSQL_KEY)

    @deprecated(version=AGENT_INSTRUMENT_VERSION, reason=AGENT_INSTRUMENT_INSTEAD)
    def register_grpc_server(self):
        """just a proxy to support deprecated method for instrumenting grpc server"""
        self._instrument(GRPC_SERVER_KEY)

    @deprecated(version=AGENT_INSTRUMENT_VERSION, reason=AGENT_INSTRUMENT_INSTEAD)
    def register_postgresql(self):
        """just a proxy to support deprecated method for instrumenting postgresql"""
        self._instrument(POSTGRESQL_KEY)

    @deprecated(version=AGENT_INSTRUMENT_VERSION, reason=AGENT_INSTRUMENT_INSTEAD)
    def register_aiohttp_client(self):
        """just a proxy to support deprecated method for instrumenting aiohttp"""
        self._instrument(AIOHTTP_CLIENT_KEY)

    @deprecated(version=AGENT_INSTRUMENT_VERSION, reason=AGENT_INSTRUMENT_INSTEAD)
    def register_flask_app(self, app=None):
        """just a proxy to support deprecated method for instrumenting flask"""
        self._instrument(FLASK_KEY, app)
