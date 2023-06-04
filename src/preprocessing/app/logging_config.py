import logging.config
from os import path

# Configure root logger object
# logging.getLogger().setLevel(logging.WARNING)

# # Disable logging from third-party modules
# for name in logging.Logger.manager.loggerDict.keys():
#     if isinstance(logging.Logger.manager.loggerDict[name], logging.Logger):
#         logger = logging.getLogger(name)
#         if logger.parent is not None:
#             if logger.parent.name == "root":
#                 logger.setLevel(logging.WARNING)

log_file_path = path.join(path.dirname(path.abspath(__file__)), "logging.conf")
logging.config.fileConfig(log_file_path)


def get_logger(name):
    return logging.getLogger("BaseConfig")
