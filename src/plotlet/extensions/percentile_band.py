"""Custom artist: percentile band (median + spread).

Given a 2-D sample (rows = x positions, cols = repetitions), draw the
median as a solid line and the band between two percentiles (default
25/75) as a translucent ribbon — the classic non-parametric
confidence-band idiom for noisy repeated-measure data.

This recipe is also a composition example: most of the work is done by
two `fill_between` + `line` calls under the hood, but we wrap them in
one artist so the call site stays a single line. The reusable bit is
the `_percentiles_from_grid` helper at the top — its output is just
data and can be fed straight to built-in `fill_between` / `line` if
you'd rather skip the artist registration.

API:
    c = pt.chart(df, aes(x="x_col", y="value_col"))
    c.add_percentile_band(qs=(0.25, 0.75))

Tidy input: one row per (x, value) observation. The artist groups by x
and computes percentiles within each group.
"""

SUMMARY = "Median line plus filled percentile ribbon for repeated-measure data."
from pathlib import Path

import plotlet as pt
from plotlet.utils import to_list, quantile, pack_opts
from plotlet.draw import polygon, polyline, rect, segment


def _percentiles_from_grid(samples, qs):
    """For each row, compute (median, q_low, q_high)."""
    med = [quantile(row, 0.5) for row in samples]
    lo = [quantile(row, qs[0]) for row in samples]
    hi = [quantile(row, qs[1]) for row in samples]
    return med, lo, hi


def pband_record(data=None, x=None, y=None, qs=None,
                 alpha=None, linewidth=None, label=None):
    if data is None or x is None or y is None:
        raise TypeError("percentile_band requires data=, x=, y=.")
    xs_all = to_list(data[x])
    ys_all = to_list(data[y])
    # Discover x positions in first-appearance order and bucket samples.
    xs: list = []
    by_x: dict = {}
    for xv, yv in zip(xs_all, ys_all):
        if xv not in by_x:
            xs.append(xv); by_x[xv] = []
        by_x[xv].append(yv)
    samples = [by_x[xv] for xv in xs]
    qs = qs if qs is not None else (0.25, 0.75)
    med, lo, hi = _percentiles_from_grid(samples, qs)
    return {"type": "percentile_band", "xs": xs, "_med": med,
            "_lo": lo, "_hi": hi,
            "opts": pack_opts(alpha=alpha, linewidth=linewidth, label=label)}


def pband_xdomain(a): return a["xs"]
def pband_ydomain(a): return a["_lo"] + a["_hi"]


def pband_draw(a, ctx):
    col = ctx.color
    fill_alpha = a["opts"].get("alpha", 0.25)
    lw = a["opts"].get("linewidth", 1.6)
    # Build the ribbon as a single closed polygon: upper boundary
    # left-to-right, lower boundary right-to-left.
    top = [(ctx.x_scale(x), ctx.y_scale(y)) for x, y in zip(a["xs"], a["_hi"])]
    bot = [(ctx.x_scale(x), ctx.y_scale(y)) for x, y in zip(a["xs"], a["_lo"])]
    pts = top + bot[::-1]
    out = [polygon(pts, fill=col, alpha=fill_alpha)]
    # Median line.
    line_pts = [(ctx.x_scale(x), ctx.y_scale(y)) for x, y in zip(a["xs"], a["_med"])]
    out.append(polyline(line_pts, color=col, width=lw))
    return "".join(out)


def pband_legend_entries(a):
    label = a["opts"].get("label")
    if not label:
        return []
    def paint(a, ctx, x0, y_mid):
        col = a["_color"]
        return (
            rect(x0, y_mid - 5, 22, 10, fill=col, alpha=0.25)
            + segment(x0, y_mid, x0 + 22, y_mid, color=col, width=1.6)
        )
    return [{"label": label, "color": a.get("_color"), "paint": paint}]


pt.add_artist(pt.ArtistSpec(
    name="percentile_band",
    record=pband_record,
    xdomain=pband_xdomain,
    ydomain=pband_ydomain,
    draw=pband_draw,
    legend_entries=pband_legend_entries,
))


def demo():
    """Build the demonstration chart with synthetic data.

    Returns a `pt.Chart` ready for `.save_svg()` or further composition."""
    import random, math
    random.seed(3)
    xs = [i * 0.5 for i in range(20)]
    # Tidy: 30 samples per x, one row each.
    rows = []
    for x in xs:
        mu = math.sin(x) + 0.05 * x
        for _ in range(30):
            rows.append({"x": x, "y": mu + random.gauss(0, 0.3 + 0.05 * x)})
    df = {k: [r[k] for r in rows] for k in rows[0]}

    c = pt.chart(df, pt.aes(x="x", y="y"))
    c.add_percentile_band(qs=(0.1, 0.9), label="10–90%")
    c.title("Median ± 10/90 percentile").xlabel("x").ylabel("y").legend(True)
    return c


if __name__ == "__main__":
    out = Path(__file__).with_suffix(".svg")
    demo().save_svg(out)
    print(f"wrote {out}")
