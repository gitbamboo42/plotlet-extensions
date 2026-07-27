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
from plotlet import aes
import plotlet.extensions          # registers all extension artists

df = {"fc": fc, "p": pvals, "gene": genes}

c = pt.chart(df, aes(x="fc", y="p", label="gene"))
c.add_volcano(fc_threshold=1.0, p_threshold=0.01)
c.save_svg("out.svg")
```

Or **import just the one you need** (same registration, lighter):

```python
import plotlet as pt
import plotlet.extensions.volcano   # registers only c.add_volcano(...)
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

> **Editable installs:** install both packages the same way. Two normal
> installs work, and two editable (`pip install -e`) checkouts work. The
> mix fails: with an editable core plotlet, a normal install of
> plotlet-extensions is invisible and `import plotlet.extensions` raises
> `ModuleNotFoundError` — install this package editable too.

## How it fits with plotlet

This distribution ships 43 domain-specific artists (volcano, manhattan, sankey,
raincloud, ma_plot, calendar_heatmap, km_curve, upset_plot, …) plus the
`plotlet.extensions` loader (`__init__.py`) that registers them all. Core
plotlet ships its built-ins under `src/plotlet/artists/` and none of
`plotlet.extensions` — this package owns the whole
`plotlet.extensions.<name>` import path.

## Gallery

Every artist is rendered in the plotlet website's
**[extensions gallery](https://gitbamboo42.github.io/plotlet/extensions.html)** —
one tile per artist, generated from each module's own `demo()` when the
site builds.

For a local preview while developing, `python gallery/_gallery.py`
renders every demo into `gallery/` and writes `gallery/index.html`;
open it in a browser. The rendered files are gitignored — the website
is the published gallery.

## Writing your own

See plotlet's [docs/EXTENDING.md](https://github.com/gitbamboo42/plotlet/blob/main/docs/EXTENDING.md).
The modules here are the reference implementations. `draw.*` is the public
SVG-emission API — don't hand-roll `<line>` / `<rect>` f-strings.
