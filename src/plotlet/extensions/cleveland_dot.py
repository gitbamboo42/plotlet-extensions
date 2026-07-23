"""Custom artist: Cleveland dot plot.

A horizontal dot at each category, optionally with a thin connecting
line from the y-axis to the dot. Cleveland's empirical work on
chart-perception found dot plots more accurately read than horizontal
bars — same data, less ink, often clearer rank ordering.

API:
    c = pt.chart(df, aes(x="value_col", y="category_col"))
    c.add_cleveland_dot(size=5, line=True, line_color="#bbbbbb")

Categories live on the y-axis (matches the chart's horizontal orientation).
Pair with `c.yscale("category", order=...)` to fix the row order.
"""

SUMMARY = "Horizontal dot at each category — Cleveland's perception-tested alternative to barh."

from pathlib import Path

import plotlet as pt
from plotlet.utils import to_list, pack_opts
from plotlet.draw import segment, circle


def cdot_record(data=None, x=None, y=None, size=None, line=None,
                line_color=None, color=None, label=None):
    if data is None or x is None or y is None:
        raise TypeError("cleveland_dot requires data=, x=, y=.")
    return {"type": "cleveland_dot",
            "labels": to_list(data[y]),
            "values": to_list(data[x]),
            "opts": pack_opts(size=size, line=line, line_color=line_color,
                              color=color, label=label)}


def cdot_xdomain(a):
    return list(a["values"]) + [0]


def cdot_ydomain(a): return a["labels"]


def cdot_draw(a, ctx):
    col = ctx.color
    r = a["opts"].get("size", 5)
    line = a["opts"].get("line", True)
    line_col = a["opts"].get("line_color", "#bbbbbb")
    out = []
    x0 = ctx.x_scale(0) if min(a["values"]) >= 0 else ctx.x_scale(min(a["values"]))
    for label, v in zip(a["labels"], a["values"]):
        py = ctx.y_scale(label)
        px = ctx.x_scale(v)
        if line:
            out.append(segment(0, py, px, py, color=line_col, width=1))
        out.append(circle(px, py, r, fill=col))
    return "".join(out)


def cdot_legend_entries(a):
    label = a["opts"].get("label")
    if not label:
        return []
    def paint(a, ctx, x0, y_mid):
        col = a["_color"]
        return (
            segment(x0, y_mid, x0 + 22, y_mid, color="#bbbbbb", width=1)
            + circle(x0 + 22, y_mid, 4, fill=col)
        )
    return [{"label": label, "color": a.get("_color"), "paint": paint}]


pt.add_artist(pt.ArtistSpec(
    name="cleveland_dot",
    record=cdot_record,
    xdomain=cdot_xdomain,
    ydomain=cdot_ydomain,
    draw=cdot_draw,
    legend_entries=cdot_legend_entries,
    force_zero_x=True,
))


def demo():
    """Build the demonstration chart with synthetic data.

    Returns a `pt.Chart` ready for `.save_svg()` or further composition."""
    cats = ["Python", "JavaScript", "TypeScript", "Rust", "Go", "C++",
            "Java", "Ruby"]
    vals = [42, 38, 27, 18, 14, 11, 22, 7]
    df = {"cat": cats, "val": vals}

    c = pt.chart(df, pt.aes(x="val", y="cat"))
    c.yscale("category", order=cats)
    c.add_cleveland_dot()
    c.title("Stack share").xlabel("% respondents")
    return c


if __name__ == "__main__":
    out = Path(__file__).with_suffix(".svg")
    demo().save_svg(out)
    print(f"wrote {out}")
