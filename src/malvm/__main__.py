"""Malvm Entrypoint."""
from .cli import malvm


def main() -> None:  # pragma: no cover
    """Main Entrypoint."""
    malvm()


if __name__ == "__main__":  # pragma: no cover
    main()
