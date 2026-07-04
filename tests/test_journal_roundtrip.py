"""Journal / JSON round-trip correctness for every extension demo.

  - In-memory:  `from_journal(to_journal(fig)).to_svg()` == `fig.to_svg()`
  - JSON:       `from_json(json.loads(json.dumps(to_json(fig)))).to_svg()`
                                                              == `fig.to_svg()`

Mirrors plotlet core's `test_journal_roundtrip.py`, but over the extension
surface: every `plotlet.extensions.<name>.demo()` must survive both round
trips byte-for-byte. `_ALL_EXTENSIONS` is discovered by walking the
`plotlet.extensions` namespace (see `test_extensions.py`), so this covers
both the modules shipped by this package and the few kept in core.
"""
from __future__ import annotations

import importlib
import json

import pytest

import plotlet as pt
from test_extensions import _ALL_EXTENSIONS


def _collect_demos():
    demos: list[tuple[str, callable]] = []
    for name in _ALL_EXTENSIONS:
        mod = importlib.import_module(f"plotlet.extensions.{name}")
        if hasattr(mod, "demo"):
            demos.append((f"extensions::{name}", mod.demo))
    return demos


PLOTS = _collect_demos()


@pytest.mark.parametrize("label,fn", PLOTS, ids=[p[0] for p in PLOTS])
def test_journal_roundtrip(label, fn):
    """Original SVG and journal-reconstructed SVG must match byte-for-byte."""
    fig = fn()
    svg_original = fig.to_svg()

    journal = pt.to_journal(fig)
    svg_from_journal = pt.from_journal(journal).to_svg()

    assert svg_original == svg_from_journal, (
        f"{label}: round-trip diverged "
        f"(original={len(svg_original)} bytes, "
        f"replayed={len(svg_from_journal)} bytes)"
    )


@pytest.mark.parametrize("label,fn", PLOTS, ids=[p[0] for p in PLOTS])
def test_json_roundtrip(label, fn):
    """JSON round-trip via `pt.to_json` / `pt.from_json`."""
    fig = fn()
    svg_original = fig.to_svg()

    blob = pt.to_json(fig)
    fig_from_json = pt.from_json(json.loads(json.dumps(blob)))
    svg_from_json = fig_from_json.to_svg()

    assert svg_original == svg_from_json, (
        f"{label}: JSON round-trip diverged "
        f"(original={len(svg_original)} bytes, "
        f"replayed={len(svg_from_json)} bytes)"
    )
