import os
from importlib import import_module

from hypertrace.agent import Agent


def modify_module_name(module_name):
    """Returns a valid modified module to get imported"""
    return ".".join(module_name.split("/"))


class HandlerError(Exception):
    pass


a = Agent()
a.instrument(None, auto_instrument=True)

path = os.environ.get("ORIG_HANDLER")

if path is None:
    raise HandlerError("ORIG_HANDLER is not defined.")

try:
    (mod_name, handler_name) = path.rsplit(".", 1)
except ValueError as e:
    raise HandlerError("Bad path '{}' for ORIG_HANDLER: {}".format(path, str(e)))

modified_mod_name = modify_module_name(mod_name)
handler_module = import_module(modified_mod_name)

lambda_handler = getattr(handler_module, handler_name)
