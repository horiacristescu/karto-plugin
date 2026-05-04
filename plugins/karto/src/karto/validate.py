"""CLI wrapper for ``python -m karto.validate``."""

from .validation import main


if __name__ == "__main__":
    raise SystemExit(main())
