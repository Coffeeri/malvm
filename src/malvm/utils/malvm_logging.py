"""This module contains the applications logger with its settings."""

# def logger(logger_name: Optional[str] = None) -> Logger:
#     if not logger_name:
#         caller_on_stack = inspect.stack()[1]
#         caller_module = inspect.getmodule(caller_on_stack[0])
#         logger_name = caller_module.__name__ if caller_module else ""
#     malvm_logger = getLogger(logger_name)
#     malvm_logger.setLevel(DEBUG)
#     file_handler = RotatingFileHandler(str(get_logfile_path() / "malvm.log"),
#                                        maxBytes=(1024 * 1024),
#                                        backupCount=10)
#     syslog_handler = SysLogHandler(address='/dev/log')
#
#     file_formatter = Formatter(
#         '%(asctime)s:%(name)s:%(levelname)s: %(message)s')
#
#     file_handler.setFormatter(file_formatter)
#
#     malvm_logger.addHandler(file_handler)
#     malvm_logger.addHandler(syslog_handler)
#     return malvm_logger
