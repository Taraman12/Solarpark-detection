import logging
import logging.config
import os

logging.config.fileConfig("src/logging_test/logging.conf")

# create logger
logger = logging.getLogger("simpleExample")

# 'application' code
logger.debug("debug message")
logger.info("info message")
logger.warning("warn message")
logger.error("error message")
logger.critical("critical message")

print(os.environ.get("DOCKERIZED"))
