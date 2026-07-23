"""Custom artist: dumbbell chart.

Two values per category — a "before" point and an "after" point — connected
by a line, with optional color encoding of the direction of change. The
go-to plot for "how did X change between two time points" or "method A vs
method B" comparisons. Easier to read than a paired bar chart for many
categories.

API:
    c = pt.chart(df, aes(y="category_col", a="col", b="col"))
    c.add_dumbbell(a_color="#1f77b4", b_color="#ff7f0e",
               up_color="#2ca02c", down_color="#d62728",
               size=4)

The `y=` column is categorical; `a=` and `b=` are numeric. The connector
picks `up_color` if `b > a`, `down_color` if `b < a`. Set
`c.yscale("category", order=...)` to keep the rows in your supplied order
(alphabetical default is rarely what you want here); plotlet places the
first category at the *top* of the y axis.
"""

SUMMARY = 'Categorical before/after: two dots connected by a line per row, color-coded by direction.'

from pathlib import Path

import plotlet as pt
from plotlet.utils import to_list, pack_opts
from plotlet.draw import segment, circle


def dumbbell_record(data=None, y=None, a=None, b=None, a_color=None,
                    b_color=None, up_color=None, down_color=None,
                    size=None, linewidth=None):
    if data is None or y is None or a is None or b is None:
        raise TypeError("dumbbell requires data=, y=, a=, b=.")
    labels = to_list(data[y])
    a_vals = to_list(data[a])
    b_vals = to_list(data[b])
    return {"type": "dumbbell", "labels": labels, "a": a_vals, "b": b_vals,
            "opts": pack_opts(a_color=a_color, b_color=b_color,
                              up_color=up_color, down_color=down_color,
                              size=size, linewidth=linewidth)}


def dumbbell_xdomain(a): return list(a["a"]) + list(a["b"])
def dumbbell_ydomain(a): return a["labels"]


def dumbbell_draw(a, ctx):
    a_col = a["opts"].get("a_color", "#1f77b4")
    b_col = a["opts"].get("b_color", "#ff7f0e")
    up_col = a["opts"].get("up_color", "#2ca02c")
    down_col = a["opts"].get("down_color", "#d62728")
    r = a["opts"].get("size", 4)
    lw = a["opts"].get("linewidth", 2)
    out = []
    for label, av, bv in zip(a["labels"], a["a"], a["b"]):
        py = ctx.y_scale(label)
        ax = ctx.x_scale(av); bx = ctx.x_scale(bv)
        line_col = up_col if bv > av else (down_col if bv < av else "#888")
        out.append(segment(ax, py, bx, py, color=line_col, width=lw))
        out.append(
            circle(ax, py, r, fill=a_col)
            + circle(bx, py, r, fill=b_col)
        )
    return "".join(out)


pt.add_artist(pt.ArtistSpec(
    name="dumbbell",
    record=dumbbell_record,
    xdomain=dumbbell_xdomain,
    ydomain=dumbbell_ydomain,
    draw=dumbbell_draw,
    uses_color_cycle=False,
))


def demo():
    """Build the demonstration chart with synthetic data.

    Returns a `pt.Chart` ready for `.save_svg()` or further composition."""
    countries = ["USA", "UK", "Germany", "France", "Japan", "Brazil",
                 "India", "China", "Mexico", "Indonesia"]
    year_a = [70, 68, 72, 71, 78, 65, 60, 67, 69, 62]
    year_b = [78, 75, 81, 80, 83, 72, 72, 79, 75, 70]
    df = {"country": countries, "y1980": year_a, "y2020": year_b}

    c = pt.chart(df, pt.aes(y="country", a="y1980", b="y2020"))
    c.yscale("category", order=countries)
    c.add_dumbbell()
    c.title("Life expectancy: 1980 → 2020").xlabel("years")
    return c


if __name__ == "__main__":
    out = Path(__file__).with_suffix(".svg")
    demo().save_svg(out)
    print(f"wrote {out}")
