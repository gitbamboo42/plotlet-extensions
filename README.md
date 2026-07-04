# plotlet-extensions

Vetted, ready-to-use plot extensions for [plotlet](https://github.com/gitbamboo42/plotlet).

## Install

```bash
pip install plotlet-extensions   # pulls in plotlet
```

## Use

**Get everything with one import** — importing `plotlet.extensions` registers
every extension artist:

```python
import plotlet as pt
import plotlet.extensions          # registers all extension artists

c = pt.chart()
c.volcano(fc, pvals, labels, fc_threshold=1.0, p_threshold=0.01)
c.save_svg("out.svg")
```

Or **import just the one you need** (same registration, lighter):

```python
import plotlet as pt
import plotlet.extensions.volcano   # registers only c.volcano(...)
```

Every extension also exposes a `demo()` that returns a fully built `pt.Chart`
with synthetic data — a useful starting point:

```python
from plotlet.extensions.volcano import demo
demo().save_svg("out.svg")
```

After `import plotlet.extensions`, `plotlet.extensions.loaded` lists what
registered and `plotlet.extensions.failed` maps any module that raised (e.g. a
missing optional dependency) to its exception.

> **Editable installs:** the one-import-loads-all convenience relies on this
> package's `__init__.py`. Under an editable (`pip install -e`) checkout of both
> repos, core's source dir shadows it, so `import plotlet.extensions` won't
> auto-load — import each extension by name during local dev. A normal
> (wheel/PyPI) install works as described above.

## How it fits with plotlet

This distribution ships ~43 domain-specific artists (volcano, manhattan, sankey,
raincloud, ecdf, ma_plot, calendar_heatmap, km_curve, upset_plot, …) plus the
`plotlet.extensions` loader (`__init__.py`) that registers them all. A handful of
extensions that core plotlet's own tests and cookbook depend on
(`numeric_bar`, `curved_tree`, `annotation_strip`, `chord_links`, `chord_ribbon`)
ship with **core plotlet** itself. Both sets live under the same
`plotlet.extensions.<name>` import path, so you never need to care which
distribution a given extension came from — install `plotlet-extensions` and
`import plotlet.extensions` gives you the whole set.

Mechanically: core plotlet exposes `plotlet.extensions` as a namespace package
(its few extensions, importable by name); installing `plotlet-extensions` adds
the rest **and** the `__init__.py` loader, which turns `import plotlet.extensions`
into "register everything".

## Gallery

`gallery/` holds a one-page visual gallery of every extension (`index.html`,
one card per artist). Ways to view it:

- **Rendered page:** enable GitHub Pages for this repo (*Settings → Pages*,
  deploy from `main`), then open
  `https://gitbamboo42.github.io/plotlet-extensions/gallery/`. GitHub does not
  render `.html` files in the repo browser, so Pages is the way to see the full
  page online.
- **Single artist:** open any `gallery/<name>.svg` directly on GitHub — it
  renders as an image.
- **Locally:** open `gallery/index.html` in a browser.

Regenerate after changing an extension with `python gallery/_gallery.py`.

## Writing your own

See plotlet's [docs/EXTENDING.md](https://github.com/gitbamboo42/plotlet/blob/main/docs/EXTENDING.md).
The modules here are the reference implementations. `draw.*` is the public
SVG-emission API — don't hand-roll `<line>` / `<rect>` f-strings.
