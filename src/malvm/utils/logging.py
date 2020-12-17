"""This module contains the applications logger with its settings."""
import logging
from logging.handlers import RotatingFileHandler, SysLogHandler

from .helper_methods import get_logfile_path

logger = logging.getLogger("malvm")

logger.setLevel(logging.DEBUG)
file_handler = RotatingFileHandler(str(get_logfile_path() / "malvm.log"),
                                   maxBytes=(1024*1024),
                                   backupCount=10)
syslog_handler = SysLogHandler(address='/dev/log')

file_formatter = logging.Formatter(
    '%(asctime)s:%(name)s:%(levelname)s: %(message)s')

file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)
logger.addHandler(syslog_handler)
