"""
we need a post-settings configured hook for django; however that isn't available, but we can wrap
the application getters of wsgi/asgi to run our instrumentation post app init
"""
import logging

from hypertrace.agent.instrumentation.instrumentation_definitions import DJANGO_KEY

logger = logging.getLogger(__name__)


def add_django_auto_instr_wrappers(agent_init, instrumentation_wrapper):
    """attempt to add wsgi/asgi wrappers if auto instrumentation is used"""
    logger.debug('attempting to add wsgi + asgi wrappers for autoinstrumentation')
    try:
        add_wsgi_wrapper(agent_init, instrumentation_wrapper)
    except:  # pylint:disable=W0702
        logger.error('django.core.wsgi.get_wsgi_application wrapping failed, django may not be instrumented')

    try:
        add_asgi_wrapper(agent_init, instrumentation_wrapper)
    except:  # pylint:disable=W0702
        logger.error('django.core.asgi.get_asgi_application wrapping failed, django may not be instrumented')


def add_wsgi_wrapper(agent_init, instrumentation_wrapper):
    """wrap the asgi wrapper get_asgi_application fn"""
    try:
        from django.core import wsgi  # pylint:disable=C0415
    except:  # pylint:disable=W0702
        logger.error('failed to import django.core.wsgi - wsgi django app may not be instrumented')
        return

    original_get_wsgi_application = wsgi.get_wsgi_application
    wsgi.get_wsgi_application = lambda: apply_wrapper_get_app_fn(original_get_wsgi_application, agent_init,
                                                                 instrumentation_wrapper)


def add_asgi_wrapper(agent_init, instrumentation_wrapper):
    """wrap the asgi wrapper get_asgi_application fn"""
    try:
        from django.core import asgi  # pylint:disable=C0415
    except:  # pylint:disable=W0702
        logger.error('failed to import django.core.asgi - asgi django app may not be instrumented')
        return

    original_get_asgi_application = asgi.get_asgi_application
    asgi.get_asgi_application = lambda: apply_wrapper_get_app_fn(original_get_asgi_application, agent_init,
                                                                     instrumentation_wrapper)

def apply_wrapper_get_app_fn(original_fn, agent_init, instrumentation_wrapper):
    """wrapper function that calls original app getter and then registers django instrumentation"""
    def ht_get_application_fn():
        app = original_fn()
        try:
            agent_init.register_library(DJANGO_KEY, instrumentation_wrapper)
        except:  # pylint:disable=W0702
            logger.error('registering django instrumentation in wsgi/asgi patch failed '
                         '- continuing without instrumenting django')
        return app

    return ht_get_application_fn()
