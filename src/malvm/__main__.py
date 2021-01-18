"""Malvm Entrypoint."""
import sys

import logging
from malvm.cli.main import malvm

log = logging.getLogger(__name__)


def add_exception_logger():
    def exception_handler(exctype, value, traceback):
        log.exception(
            f"EXCEPTION: \n"
            f"TYPE: {exctype.__name__}\n"
            f"VALUE: {value}\n"
            f"TRACEBACK: {traceback}"
        )

    sys.excepthook = exception_handler


def main() -> None:  # pragma: no cover
    """Main Entrypoint."""
    add_exception_logger()
    malvm()


if __name__ == "__main__":  # pragma: no cover
    main()
