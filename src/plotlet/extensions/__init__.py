"""Batteries-included loader for plotlet's extension artists.

With `plotlet-extensions` installed, importing `plotlet.extensions` (or any
single extension under it) registers **every** extension artist at once:

    import plotlet as pt
    import plotlet.extensions          # registers all extension artists

    c = pt.chart()
    c.volcano(...)                     # any extension method now works

This module ships in the `plotlet-extensions` distribution. Core plotlet ships
a few extensions under the same `plotlet.extensions` namespace but without this
`__init__`, so a core-only install leaves them lazy (import each by name). Once
`plotlet-extensions` is installed, this loader takes over and eagerly registers
the whole set.

Introspect what happened:

    plotlet.extensions.loaded   # list[str]  — modules that registered
    plotlet.extensions.failed   # dict[str, Exception] — any that raised
                                #   (e.g. a missing optional dependency)

Composition-helper extensions (e.g. `jointplot`, `pair_plot`) register nothing
on import — call them as functions: `from plotlet.extensions.jointplot import
jointplot`.
"""
from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

__all__ = ["loaded", "failed"]


def _module_names() -> list[str]:
    """Every extension module name under `plotlet.extensions`.

    Union of the installed namespace path (all modules in a wheel install; the
    core-shipped extensions in any install) and this package's own directory
    (robust under editable installs whose import hook doesn't populate the
    namespace `__path__`).
    """
    names: set[str] = set()
    for info in pkgutil.iter_modules(__path__):
        if not info.name.startswith("_"):
            names.add(info.name)
    here = Path(__file__).resolve().parent
    for py in here.glob("*.py"):
        if py.stem != "__init__" and not py.stem.startswith("_"):
            names.add(py.stem)
    return sorted(names)


def _load_all() -> tuple[list[str], dict[str, Exception]]:
    ok: list[str] = []
    bad: dict[str, Exception] = {}
    for name in _module_names():
        try:
            importlib.import_module(f"{__name__}.{name}")
            ok.append(name)
        except Exception as exc:  # noqa: BLE001 — one bad optional dep shouldn't sink the rest
            bad[name] = exc
    return ok, bad


loaded, failed = _load_all()
