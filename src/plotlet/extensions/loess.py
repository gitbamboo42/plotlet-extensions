"""Custom artist: LOESS smoother (statsmodels-backed).

Locally-weighted regression smoother — fits a smooth curve through
noisy `(x, y)` data without assuming a parametric form. Uses
`statsmodels.nonparametric.lowess` under the hood, which gives:
  - degree 1 local linear fits
  - 3 robustifying iterations by default (downweight outliers)
  - configurable `frac` (the "span" — fraction of points used per fit)

API:
    c = pt.chart(df, aes(x="col", y="col"))
    c.add_loess(frac=0.5, it=3)

Earlier versions of this recipe inlined a degree-1, no-robustness
LOESS in pure Python (no scipy dep). The statsmodels version is
strictly more flexible and more robust to outliers.
"""

SUMMARY = "LOESS local-regression smoother via statsmodels lowess (degree 1 + robustifying iterations)."

from pathlib import Path

import plotlet as pt
from plotlet.draw import polyline, segment
from plotlet.utils import to_list, pack_opts


def loess_record(data=None, x=None, y=None, frac=None, span=None, it=None,
                 linewidth=None, label=None):
    if data is None or x is None or y is None:
        raise TypeError("loess requires data=, x=, y=.")
    xs = to_list(data[x]); ys = to_list(data[y])
    if frac is None:
        frac = span if span is not None else 0.5
    if it is None:
        it = 3
    opts = pack_opts(linewidth=linewidth, label=label)
    if not xs:
        return {"type": "loess", "_grid": [], "_fit": [], "opts": opts}
    try:
        from statsmodels.nonparametric.smoothers_lowess import lowess
    except ImportError as e:
        raise ImportError(
            "c.loess requires statsmodels, which is not a hard dependency "
            "of plotlet. Install it with `pip install statsmodels`."
        ) from e
    smoothed = lowess(ys, xs, frac=frac, it=it, return_sorted=True)
    grid = smoothed[:, 0].tolist()
    fit = smoothed[:, 1].tolist()
    return {"type": "loess", "_grid": grid, "_fit": fit, "opts": opts}


def loess_xdomain(a): return a["_grid"]
def loess_ydomain(a): return a["_fit"]


def loess_draw(a, ctx):
    col = ctx.color
    lw = a["opts"].get("linewidth", 2)
    pts = [(ctx.x_scale(x), ctx.y_scale(y))
           for x, y in zip(a["_grid"], a["_fit"]) if y == y]
    if len(pts) < 2:
        return ""
    return polyline(pts, color=col, width=lw)


def loess_legend_entries(a):
    label = a["opts"].get("label")
    if not label:
        return []
    def paint(a, ctx, x0, y_mid):
        return segment(x0, y_mid, x0 + 22, y_mid, color=a["_color"], width=2)
    return [{"label": label, "color": a.get("_color"), "paint": paint}]


pt.add_artist(pt.ArtistSpec(
    name="loess",
    record=loess_record,
    xdomain=loess_xdomain,
    ydomain=loess_ydomain,
    draw=loess_draw,
    legend_entries=loess_legend_entries,
))


def demo():
    """Build the demonstration chart with synthetic data.

    Returns a `pt.Chart` ready for `.save_svg()` or further composition."""
    import random, math
    random.seed(0)
    n = 200
    xs = [i * 0.05 for i in range(n)]
    ys = [math.sin(x) + 0.4 * math.sin(3 * x) + random.gauss(0, 0.3) for x in xs]
    # Throw in a couple of outliers to demonstrate the robust pass.
    ys[20] += 4; ys[150] -= 5
    df = {"x": xs, "y": ys}

    c = pt.chart(df, pt.aes(x="x", y="y"))
    c.add_scatter(size=1.5, alpha=0.5, label="data")
    c.add_loess(frac=0.3, label="LOESS (frac=0.3)")
    c.add_loess(frac=0.7, label="LOESS (frac=0.7)")
    c.title("LOESS smoother").xlabel("x").ylabel("y").legend(True)
    return c


if __name__ == "__main__":
    out = Path(__file__).with_suffix(".svg")
    demo().save_svg(out)
    print(f"wrote {out}")
