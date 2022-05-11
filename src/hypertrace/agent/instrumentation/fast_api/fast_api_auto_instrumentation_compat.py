"""
we need a post-settings configured hook for django; however that isn't available, but we can wrap
the application getters of wsgi/asgi to run our instrumentation post app init
"""
import logging

from hypertrace.agent.instrumentation.instrumentation_definitions import FAST_API_KEY

logger = logging.getLogger(__name__)
_PATCHED_SETUP = False
_ORIGINAL_SETUP = None

def add_fast_api_auto_instr_wrappers(agent_init, instrumentation_wrapper):
    """wrap the fast api initializer"""
    logger.debug('attempting to add fast api initializer wrapper for autoinstrumentation')
    try:
        global _PATCHED_SETUP  # pylint:disable=W0603
        if not _PATCHED_SETUP:  # pylint:disable=W0603
            add_setup_wrapper(agent_init, instrumentation_wrapper)
            _PATCHED_SETUP = True
    except:  # pylint:disable=W0702
        logger.error('django.core.wsgi.get_wsgi_application wrapping failed, django may not be instrumented')


def add_setup_wrapper(agent_init, instrumentation_wrapper):
    """wrap the asgi wrapper get_asgi_application fn"""
    try:
        import fastapi  # pylint:disable=C0415
    except:  # pylint:disable=W0702
        logger.error('failed to import fastapi -fastapi app may not be instrumented')
        return
    global _ORIGINAL_SETUP  # pylint:disable=W0603
    _ORIGINAL_SETUP = fastapi.FastAPI.setup
    fastapi.FastAPI.setup = lambda fastapi_app: apply_wrapper_setup_fn(_ORIGINAL_SETUP, fastapi_app,
                                                                       agent_init,
                                                                       instrumentation_wrapper)

def unwrap():
    """Used to unwrap the fastapi setup function"""
    try:
        import fastapi  # pylint:disable=C0415
    except:  # pylint:disable=W0702
        logger.error('failed to import fastapi -fastapi app may not be instrumented')
        return
    fastapi.FastAPI.setup = _ORIGINAL_SETUP
    global _PATCHED_SETUP # pylint:disable=W0603
    _PATCHED_SETUP = False


def apply_wrapper_setup_fn(original_fn, fastapi_app, agent_init, instrumentation_wrapper):
    """wrapper function that calls original app getter and then registers django instrumentation"""

    # We need to run instrumentation first to inject middleware before we call the original function
    # otherwise middleware stack changes are not applied
    def ht_setup_fn():
        try:
            instrumentation_wrapper.with_app(fastapi_app)
            agent_init.register_library(FAST_API_KEY, instrumentation_wrapper)
        except:  # pylint:disable=W0702
            logger.error('registering fastapi instrumentation in fastapi setup patch failed '
                         '- continuing without instrumenting fastapi')
        app = original_fn(fastapi_app)
        return app

    return ht_setup_fn()
