"""Build gallery/index.html — single-page visual gallery of every extension demo.

Module sources live in `../src/plotlet/extensions/<name>.py`; the rendered
SVGs and the index page live here in `gallery/`. For each module:
  - read SUMMARY from the source (no execution)
  - render `demo().to_svg()` into `gallery/<name>.svg` if missing or stale
  - embed the SVG inline in a card on the gallery page

Only the modules shipped by this package are covered; the handful of
extensions kept in core plotlet won't appear here.

Run:  python gallery/_gallery.py
"""
from __future__ import annotations

import ast
import html
import importlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULES = HERE.parent / "src" / "plotlet" / "extensions"


def _summary(py_path: Path) -> str:
    """Read SUMMARY = '...' from the file without executing it."""
    tree = ast.parse(py_path.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "SUMMARY":
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        return node.value.value
    return ""


def _ensure_svg(svg_path: Path, py_path: Path) -> bool:
    """Render `<name>.demo().to_svg()` into `svg_path` if missing or stale.
    Returns True if the SVG is present afterwards."""
    if svg_path.exists() and svg_path.stat().st_mtime >= py_path.stat().st_mtime:
        return True
    name = py_path.stem
    print(f"  rendering {name}")
    try:
        mod = importlib.import_module(f"plotlet.extensions.{name}")
        svg_path.write_text(mod.demo().to_svg())
    except Exception as e:  # noqa: BLE001 — best-effort gallery build
        print(f"  ! {name} failed: {e}")
        return False
    return svg_path.exists()


# Extensions live in this package's source tree; link "view source" at them
# on GitHub so the links work from a Pages deploy.
SRC_BASE = "https://github.com/gitbamboo42/plotlet-extensions/blob/main/src/plotlet/extensions"


CSS = """
* { box-sizing: border-box; }
body {
  margin: 0; padding: 32px 24px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
  color: #222;
  background: #fafafa;
}
h1 { margin: 0 0 8px; font-size: 28px; font-weight: 600; }
p.lead { margin: 0 0 28px; color: #666; max-width: 760px; line-height: 1.5; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
}
.card {
  background: white;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  overflow: hidden;
  display: flex; flex-direction: column;
}
.card h2 {
  margin: 0; padding: 12px 16px 4px;
  font-size: 15px; font-weight: 600; font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}
.card p {
  margin: 0; padding: 0 16px 12px;
  font-size: 13px; color: #555; line-height: 1.45;
  flex-grow: 1;
}
.card .svgwrap {
  background: #fff; padding: 8px; border-top: 1px solid #f0f0f0;
}
.card img { width: 100%; height: auto; max-height: 280px; display: block; }
.card a {
  display: block; padding: 8px 16px; font-size: 12px;
  color: #555; text-decoration: none;
  border-top: 1px solid #f0f0f0;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}
.card a:hover { background: #f7f7f7; color: #000; }
.section { margin: 32px 0 12px; font-size: 12px; font-weight: 600;
           text-transform: uppercase; letter-spacing: 0.06em; color: #888; }
"""


# Same section taxonomy as cookbook/, but resolved as flat <name>.py files.
SECTIONS = [
    ("Common", [
        "errorbar", "boxplot", "violin", "ecdf", "density_1d",
        "regression", "loess", "horizontal_bar", "cleveland_dot",
        "stacked_bar", "stacked_area", "grouped_bar", "dumbbell",
        "text_label",
    ]),
    ("Distributions and stats", [
        "strip", "swarm", "ridge", "qq_plot", "freqpoly",
        "percentile_band", "bland_altman", "boxenplot", "rug",
        "raincloud", "split_violin", "pointplot", "crossbar",
        "jointplot", "pair_plot",
    ]),
    ("Big-data scatter", ["hexbin", "contour", "kde_2d"]),
    ("Bio / omics", ["volcano", "ma_plot", "manhattan", "gene_arrow"]),
    ("Heatmaps", [
        "clustermap", "bubble_grid",
        "calendar_heatmap", "mosaic",
    ]),
    ("Clinical", ["km_curve", "forest_plot", "funnel_plot"]),
    ("ML evaluation", [
        "roc_curve", "pr_curve", "confusion_matrix", "calibration_plot",
    ]),
    ("Multivariate", ["pca_biplot", "parallel_coordinates", "residual_diagnostics"]),
    ("Categorical / comparison", [
        "slope_chart", "bump", "waterfall", "sales_funnel", "diverging_bar",
        "pyramid_plot", "lollipop", "numeric_bar",
    ]),
    ("Time / event", ["eventplot"]),
    ("Dashboards", ["horizon"]),
    ("Set analysis", ["upset_plot"]),
    ("Flows", ["sankey", "alluvial"]),
    ("Annotation overlays", ["significance_brackets"]),
]


def main():
    cards_by_section: dict[str, list[str]] = {}
    listed = set()
    for section, names in SECTIONS:
        cards = []
        for name in names:
            py = MODULES / f"{name}.py"
            svg = HERE / f"{name}.svg"
            if not py.exists():
                continue
            if not _ensure_svg(svg, py):
                continue
            summary = _summary(py)
            cards.append(
                f'<div class="card">'
                f'<h2>c.{html.escape(name)}</h2>'
                f'<p>{html.escape(summary)}</p>'
                f'<div class="svgwrap"><img src="{name}.svg" loading="lazy" alt="c.{html.escape(name)}"></div>'
                f'<a href="{SRC_BASE}/{name}.py">view source →</a>'
                f'</div>'
            )
            listed.add(name)
        if cards:
            cards_by_section[section] = cards
    # Pick up any flat-file extensions that aren't in the section index.
    extras = []
    for py in sorted(MODULES.glob("*.py")):
        if py.name.startswith("_"):
            continue
        name = py.stem
        if name in listed:
            continue
        svg = HERE / f"{name}.svg"
        if not _ensure_svg(svg, py):
            continue
        extras.append(
            f'<div class="card"><h2>c.{html.escape(name)}</h2>'
            f'<p>{html.escape(_summary(py))}</p>'
            f'<div class="svgwrap"><img src="{name}.svg" loading="lazy" alt="c.{html.escape(name)}"></div>'
            f'<a href="{SRC_BASE}/{name}.py">view source →</a></div>'
        )
    if extras:
        cards_by_section["Other"] = extras

    body = []
    for section, cards in cards_by_section.items():
        body.append(f'<div class="section">{html.escape(section)}</div>')
        body.append('<div class="grid">' + "".join(cards) + '</div>')

    out_path = HERE / "index.html"
    out_path.write_text(
        f'<!doctype html><meta charset="utf-8"><title>plotlet-extensions</title>'
        f'<style>{CSS}</style>'
        f'<h1>plotlet-extensions</h1>'
        f'<p class="lead">One-file domain-specific artists for plotlet — '
        f'<code>import plotlet.extensions.&lt;name&gt;</code> registers the method, then '
        f'<code>c.&lt;name&gt;(...)</code>. Copy a module, swap your data, or register your own '
        f'with <code>pt.add_artist(...)</code>.</p>'
        + "".join(body)
    )
    print(f"\nwrote {out_path}")
    print(f"  {len(listed) + len(extras)} extensions")


if __name__ == "__main__":
    main()
