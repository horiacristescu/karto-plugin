"""CLI wrapper for ``python -m karto.score``."""

from .scoring import main


if __name__ == "__main__":
    raise SystemExit(main())
