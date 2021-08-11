"""
Logging configuration
"""
import logging
import os
import sys
import traceback

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
        if 'HT_LOG_LEVEL' in os.environ:
            ht_log_level = os.environ['HT_LOG_LEVEL']
            log_level = _LOG_LEVEL.get(ht_log_level, log_level)

        logger_.setLevel(log_level)
        logger_.addHandler(screen_handler)
        return logger_
    except Exception as err:  # pylint: disable=W0703
        print('Failed to customize logger: exception=%s, stacktrace=%s',
              err,
              traceback.format_exc())
        return None
