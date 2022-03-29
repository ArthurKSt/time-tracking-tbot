import logging

from constants.config import LOG_DIR

filename = LOG_DIR+"bot.log" if LOG_DIR != "" else ""
logging.basicConfig(filename=filename, level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("\n\nINFO:start log")
