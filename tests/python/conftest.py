"""Load the role scripts and tools, which are not importable packages, as modules."""

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType

REPOSITORY = Path(__file__).parents[2]
ROLES = REPOSITORY / "roles"

#: Plugins sharing fixtures between test modules.
pytest_plugins = ("serial_display_fakes",)


def load_module(path: Path) -> ModuleType:
    """Import a Python file as a module named after its stem."""
    spec = spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    return module


def load_script(relative_path: str) -> ModuleType:
    """Import a script of a role by its path relative to `roles/`."""
    return load_module(ROLES / relative_path)


def load_tool(name: str) -> ModuleType:
    """Import a script of `tools/` by its file name."""
    return load_module(REPOSITORY / "tools" / name)
