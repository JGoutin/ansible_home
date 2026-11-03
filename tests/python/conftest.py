"""Load the role scripts, which are not importable packages, as modules."""

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType

ROLES = Path(__file__).parents[2] / "roles"


def load_script(relative_path: str) -> ModuleType:
    """Import a script of a role by its path relative to `roles/`."""
    path = ROLES / relative_path
    spec = spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    return module
