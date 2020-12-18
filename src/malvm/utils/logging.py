"""This module contains the applications logger with its settings."""
from logging import getLogger, Formatter, DEBUG
from logging.handlers import RotatingFileHandler, SysLogHandler

from .helper_methods import get_logfile_path

logger = getLogger("malvm")

logger.setLevel(DEBUG)
file_handler = RotatingFileHandler(str(get_logfile_path() / "malvm.log"),
                                   maxBytes=(1024 * 1024),
                                   backupCount=10)
syslog_handler = SysLogHandler(address='/dev/log')

file_formatter = Formatter(
    '%(asctime)s:%(name)s:%(levelname)s: %(message)s')

file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)
logger.addHandler(syslog_handler)
