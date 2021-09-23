"""
WSGI config for testapp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from hypertrace.agent import Agent

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testapp.settings')
TEST_AGENT_INSTANCE = Agent()
TEST_AGENT_INSTANCE.register_django()
application = get_wsgi_application()
