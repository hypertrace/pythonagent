import logging
import sys
import traceback


def get_logger(name):
    try:
        formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        handler = logging.FileHandler('agent.log', mode='a')
        handler.setFormatter(formatter)
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.addHandler(screen_handler)

        return logger
    except:
        print('Failed to customize logger: exception=%s, stacktrace=%s' % (
            sys.exc_info()[0],
            traceback.format_exc()))