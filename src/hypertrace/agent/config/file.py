'''File config loader'''

import os
import logging
import traceback
import yaml


logger = logging.getLogger(__name__)  # pylint: disable=C0103


def load_config_from_file(filepath):
    """
    Returns the config loaded from a provided config file
    """
    logger.debug(
        'HT_CONFIG_FILE is set %s. Attempting to load the config file', filepath)
    try:
        path = os.path.abspath(filepath)

        file = open(path, 'r') # pylint: disable=R1732
        from_file_config = yaml.safe_load(file)
        file.close()

        logger.debug('Successfully load config from %s', path)

        return from_file_config
    except Exception as err:  # pylint: disable=W0703
        logger.error('Failed to load HT_CONFIG_FILE: exception=%s, stacktrace=%s',
                     err,
                     traceback.format_exc())
        logger.info('Loading default configuration.')
        return {}
