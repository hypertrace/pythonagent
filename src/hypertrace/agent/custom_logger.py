"""
Logging configuration
"""
import logging
import sys
import traceback

from hypertrace.env_var_settings import get_env_value

_LOG_LEVEL = {
    None: logging.INFO,
    '': logging.INFO,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'CRTITICAL': logging.CRITICAL,
    'NOTSET': logging.NOTSET
}

def get_custom_logger(name: str) -> logging.Logger:
    '''Agent logger configuration'''
    try:
        formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)
        log_level = logging.INFO
        logger_ = logging.getLogger(name)
        env_value = get_env_value('LOG_LEVEL')
        if env_value:
            log_level = _LOG_LEVEL.get(env_value, log_level)

        logger_.setLevel(log_level)
        logger_.addHandler(screen_handler)
        return logger_
    except Exception as err:  # pylint: disable=W0703
        print('Failed to customize logger: exception=%s, stacktrace=%s',
              err,
              traceback.format_exc())
        return None
