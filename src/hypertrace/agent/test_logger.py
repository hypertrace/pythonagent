'''Unittest for logging'''

import logging
import codecs

def test_register():


    # Unicode string
    i = b'\xe9'
    logger = logging.getLogger("asdf")
    logger.error("foo %s", str(i))

    # Logging gives a Traceback
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    handler = logging.FileHandler('/tmp/out', 'w', 'utf-8')
    handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    # I've also tried nixing setFormatter and going with the default
    log.addHandler(handler)
    log.debug(u"process_clusters: From CSV: %s", i)