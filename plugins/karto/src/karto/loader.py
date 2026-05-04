"""Load user-authored SSP modules from disk."""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
from types import ModuleType


class LoadError(RuntimeError):
    """Raised when an SSP module cannot be loaded."""


def load_module(path: str | Path) -> ModuleType:
    module_path = Path(path).expanduser().resolve()
    if not module_path.exists():
        raise LoadError(f"SSP module not found: {module_path}")
    if not module_path.is_file():
        raise LoadError(f"SSP module is not a file: {module_path}")

    digest = hashlib.sha256(str(module_path).encode()).hexdigest()[:8]
    module_name = f"karto._ssp_{digest}"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise LoadError(f"Could not create import spec for: {module_path}")

    module = importlib.util.module_from_spec(spec)
    try:
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    except Exception as exc:
        raise LoadError(f"Failed to import SSP module {module_path}: {exc}") from exc
    finally:
        sys.modules.pop(module_name, None)

    return module
