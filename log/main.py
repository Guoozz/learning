import logging
from log.test import some_func


logger = logging.getLogger("a")

logger.debug("call some_func")
some_func()
logger.debug("some_func complete")
