"""Malvm Entrypoint."""
import logging
import sys

from .cli import malvm

log = logging.getLogger()


def add_exception_logger():
    def exception_handler(exctype, value, traceback):
        log.exception(
            f"EXCEPTION: \n"
            f"TYPE: {exctype.__name__}\n"
            f"VALUE: {value}\n"
            f"TRACEBACK: {str(traceback.tr)}"
        )

    sys.excepthook = exception_handler


def main() -> None:  # pragma: no cover
    """Main Entrypoint."""
    add_exception_logger()
    malvm()


if __name__ == "__main__":  # pragma: no cover
    main()
