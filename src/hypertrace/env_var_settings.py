"""
Used to override env var prefix
these are separated out to prevent any classes from being imported before being customized
"""

import os

_DEFAULT_ENV_VAR_PREFIX = 'HT'
ENV_VAR_PREFIXES = [_DEFAULT_ENV_VAR_PREFIX]


def get_env_value(target_key):
    """checks env for given target_key with any configured prefix"""
    for prefix in ENV_VAR_PREFIXES:
        env_var_key = f"{prefix}_{target_key}"
        if env_var_key in os.environ:
            return os.environ[env_var_key]
    return None
