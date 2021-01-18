# from malvm.cli.utils import print_info
# from malvm.utils.malvm_logging import logger
#
#
# def test_logger_name():
#     logger().debug("Test message")
#     assert logger().name == __name__
#
#
# def test_caller_logger_name():
#     print_info("Test message")
#     expected_logger_name = __name__
#     actual_logger_name = ""
#     assert expected_logger_name == actual_logger_name
import logging

from malvm.utils.malvm_logging import setup_logging


def test_logger(caplog):
    setup_logging()
    log = logging.getLogger(__name__)
    log.error("test")
