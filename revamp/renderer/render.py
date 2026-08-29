"""
BrainActive v0.4.1 SVG/visual renderer.

Focused renderer for the visual_spec types present in the frozen baseline.
Single source of truth: each layout returns a list of PRIMITIVES in a normalised
coordinate space; two serializers emit (a) a PNG (for visual QA in this environment)
and (b) an SVG string (for the React-Native app via react-native-svg).

NOT a general-purpose graphics framework. Add a new spec `type` -> add one layout fn.
"""

import json
import math
import os
import re
import sys
from PIL import Image, ImageDraw, ImageFont

RED = "#e4572e"
BLUE = "#4a90d9"
GREEN = "#3bb273"
YELLOW = "#f4c430"
PURPLE = "#9b5de5"
GRAY = "#9aa0a6"
DARK = "#2b2d42"
WHITE = "#ffffff"
BG = "#fbfcfe"

COLORS = {"red": RED, "blue": BLUE, "green": GREEN, "yellow": YELLOW,
          "purple": PURPLE, "gray": GRAY, "dark": DARK, "white": WHITE}
STROKE = DARK
SW = 3


def _col(c):
    if c is None:
        return None
    return COLORS.get(c, c)


def reg_poly(cx, cy, r, sides, rot_deg, fill, stroke=STROKE, sw=SW):
    pts = []
    for i in range(sides):
        a = math.radians(rot_deg + i * 360.0 / sides)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return {"t": "poly", "points": pts, "fill": _col(fill), "stroke": _col(stroke), "sw": sw}


def poly(pts, fill, stroke=STROKE, sw=SW):
    return {"t": "poly", "points": pts, "fill": _col(fill), "stroke": _col(stroke), "sw": sw}


def circle(cx, cy, r, fill, stroke=STROKE, sw=SW):
    return {"t": "circle", "cx": cx, "cy": cy, "r": r, "fill": _col(fill), "stroke": _col(stroke), "sw": sw}


def rect(x, y, w, h, fill, stroke=STROKE, sw=SW, rx=8):
    return {"t": "rect", "x": x, "y": y, "w": w, "h": h, "fill": _col(fill), "stroke": _col(stroke), "sw": sw, "rx": rx}


def line(x1, y1, x2, y2, stroke=STROKE, sw=SW):
    return {"t": "line", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "stroke": _col(stroke), "sw": sw}


def text(x, y, s, size=20, fill=DARK, anchor="middle", weight="bold"):
    return {"t": "text", "x": x, "y": y, "s": s, "size": size, "fill": _col(fill), "anchor": anchor, "weight": weight}


def arc(cx, cy, r, a0, a1, stroke=STROKE, sw=SW):
    return {"t": "arc", "cx": cx, "cy": cy, "r": r, "a0": a0, "a1": a1, "stroke": _col(stroke), "sw": sw}


def dots(cx, cy, n, spread=16, r=4, fill=DARK):
    out = []
    if n <= 0:
        return out
    start = cx - (n - 1) * spread / 2.0
    for i in range(n):
        out.append(circle(start + i * spread, cy, r, fill, stroke=None, sw=0))
    return out


def chevron(cx, cy, size, dir_deg, color=STROKE, sw=SW):
    a = math.radians(dir_deg)
    tip = (cx + size * math.cos(a), cy + size * math.sin(a))
    left = (cx + size * 0.7 * math.cos(a + 2.5), cy + size * 0.7 * math.sin(a + 2.5))
    right = (cx + size * 0.7 * math.cos(a - 2.5), cy + size * 0.7 * math.sin(a - 2.5))
    return poly([tip, left, right], color, stroke=None, sw=0)


def caption(id, level):
    return text(180, 244, id + "  [" + level + "]", size=13, fill=GRAY, anchor="middle", weight="normal")


def L_layout(spec):
    prims = []
    x0, y0, s = 120, 70, 60
    # before: corner at top-left = top row + left column
    prims += [rect(x0, y0, s, s, GRAY, stroke=None, sw=0, rx=4),
              rect(x0 + s, y0, s, s, GRAY, stroke=None, sw=0, rx=4),
              rect(x0, y0 + s, s, s, GRAY, stroke=None, sw=0, rx=4)]
    prims.append(arc(180, 130, 80, -150, -30, stroke=BLUE, sw=4))
    prims.append(chevron(180 + 80 * math.cos(math.radians(-30)), 130 + 80 * math.sin(math.radians(-30)), 14, -30, BLUE))
    rx0, ry0 = 120, 70
    # after (90 CW): corner at top-right = top row + right column
    prims += [rect(rx0, ry0, s, s, RED, rx=4),
              rect(rx0 + s, ry0, s, s, RED, rx=4),
              rect(rx0 + s, ry0 + s, s, s, RED, rx=4)]
    prims.append(text(180, 30, "L-shape after 90 deg clockwise", size=18, fill=DARK))
    return prims, 360, 262


def rotation_sequence_layout(spec):
    prims = []
    start = spec.get("start", "up")
    steps = spec.get("steps", spec.get("steps_shown", 3))
    dirs = {"up": -90, "right": 0, "down": 90, "left": 180}
    if "step7" in spec:
        s7 = spec["step7"]
        prims.append(text(180, 24, "Cycle up->right->down->left. Step 7 = " +
                          str(s7.get("direction")) + ", " + str(s7.get("colour")), size=15))
        col7 = COLORS.get(s7.get("colour"), DARK)
        prims.append(chevron(180, 130, 26, dirs.get(s7.get("direction"), -90), col7))
        return prims, 360, 262
    d = dirs.get(start, -90)
    n = max(int(steps) + 1, 4)
    seq = [(d + i * 90) % 360 for i in range(n)]
    xs = [55 + i * (250 / max(len(seq) - 1, 1)) for i in range(len(seq))]
    prims.append(text(180, 24, "Rotation sequence (90 deg each step)", size=16))
    for i, ang in enumerate(seq):
        prims.append(chevron(xs[i], 130, 24, ang, DARK))
        prims.append(text(xs[i], 175, "step " + str(i + 1), size=12, fill=GRAY))
    return prims, 360, 262


def reflection_layout(spec):
    prims = []
    prims.append(text(180, 24, "Vertical mirror (left-right flip)", size=16))
    prims.append(line(180, 50, 180, 210, stroke=GRAY, sw=2))
    prims.append(text(110, 130, spec.get("source", "b"), size=70, fill=DARK))
    prims.append(text(250, 130, spec.get("result", "d"), size=70, fill=BLUE))
    return prims, 360, 262


def cube_faces_layout(spec):
    prims = []
    fx, fy, fs = 110, 120, 90
    prims.append(rect(fx, fy, fs, fs, WHITE, rx=4))
    prims.append(poly([(fx, fy), (fx + 45, fy - 40), (fx + 45 + fs, fy - 40), (fx + fs, fy)], WHITE, STROKE, SW))
    prims.append(poly([(fx + fs, fy), (fx + 45 + fs, fy - 40), (fx + 45 + fs, fy - 40 + fs), (fx + fs, fy + fs)], WHITE, STROKE, SW))
    prims.append(text(fx + fs / 2, fy + fs / 2, spec.get("front", "F"), size=22, fill=RED))
    prims.append(text(fx + 22, fy - 20, spec.get("top", "T"), size=18, fill=BLUE))
    prims.append(text(fx + fs + 22, fy + fs / 2, spec.get("right", "R"), size=18, fill=GREEN))
    prims.append(text(180, 235, "front=" + str(spec.get("front")) + " top=" + str(spec.get("top")) +
                      " right=" + str(spec.get("right")) + " back=" + str(spec.get("opposite_front")), size=13, fill=GRAY))
    return prims, 360, 262


def cube_net_layout(spec):
    prims = []
    layout = spec.get("layout")
    front = spec.get("front", "Y")
    back = spec.get("back", "U")
    cell = 46
    ox, oy = 150, 40
    prims.append(text(180, 24, "Cube net (fold with " + str(front) + " as front)", size=15))
    labels = {(0, 1): "W", (1, 0): "X", (1, 1): front, (1, 2): "Z", (2, 1): "V", (3, 1): back}
    for r in range(4):
        for c in range(3):
            if layout[r][c] == "":
                continue
            x = ox + (c - 1) * cell
            y = oy + r * cell
            prims.append(rect(x, y, cell, cell, WHITE, rx=4))
            prims.append(text(x + cell / 2, y + cell / 2, labels.get((r, c), "?"), size=20, fill=DARK))
    prims.append(text(180, 238, "back face (opposite " + str(front) + ") = " + str(back), size=13, fill=GRAY))
    return prims, 360, 262


def rotation_3d_layout(spec):
    prims = []
    star_after = spec.get("star_after", "right")
    fx, fy, fs = 110, 110, 100
    prims.append(rect(fx, fy, fs, fs, WHITE, rx=4))
    prims.append(poly([(fx, fy), (fx + 50, fy - 45), (fx + 50 + fs, fy - 45), (fx + fs, fy)], WHITE, STROKE, SW))
    prims.append(poly([(fx + fs, fy), (fx + 50 + fs, fy - 45), (fx + 50 + fs, fy - 45 + fs), (fx + fs, fy + fs)], WHITE, STROKE, SW))
    prims.append(text(fx + fs / 2, fy + fs / 2, "STAR", size=18, fill=RED))
    prims.append(text(fx + 26, fy - 22, "DOT", size=15, fill=BLUE))
    prims.append(text(fx + fs + 26, fy + fs / 2, "STAR", size=15, fill=GREEN))
    prims.append(text(180, 235, "Rotate right 90 deg -> star moves to " + str(star_after), size=14, fill=GRAY))
    return prims, 360, 262


def shape_transformation_layout(spec):
    prims = []
    seq = spec.get("sequence", [])
    prims.append(text(180, 24, "Shape transformation (add side + alternate colour)", size=14))
    n = len(seq)
    xs = [55 + i * (250 / max(n - 1, 1)) for i in range(n)]
    for i, token in enumerate(seq):
        m = re.match(r"(\w+)\s+(\w+)\((\d+)\)", token)
        if not m:
            continue
        shp, col, sides = m.group(1), m.group(2), int(m.group(3))
        prims.append(reg_poly(xs[i], 120, 34, sides, -90 if shp in ("triangle", "pentagon") else 0, col))
        prims.append(text(xs[i], 175, token, size=12, fill=GRAY))
        if i < n - 1:
            prims.append(text((xs[i] + xs[i + 1]) / 2, 120, "->", size=18, fill=DARK))
    return prims, 360, 262


def combine_shapes_layout(spec):
    prims = []
    parts = spec.get("parts", [])
    prims.append(text(180, 24, "Combine shapes (positions matter)", size=15))
    bx, by, bs = 130, 110, 90
    prims.append(rect(bx, by, bs, bs, WHITE, rx=6))
    lab = ""
    if "triangle_left" in parts:
        prims.append(poly([(bx - 30, by), (bx - 30, by + bs), (bx, by + bs / 2)], RED))
        lab += "triangle left; "
    if "circle_right" in parts:
        prims.append(circle(bx + bs + 30, by + bs / 2, 26, BLUE))
        lab += "circle right; "
    if "triangle_top" in parts:
        prims.append(poly([(bx + bs / 2, by - 30), (bx, by), (bx + bs, by)], RED))
    prims.append(text(180, 230, lab.strip(), size=13, fill=GRAY))
    return prims, 360, 262


def _parse_fig(s):
    if s is None:
        return None
    s = str(s).strip().lower()
    if s == "?":
        return None
    s = re.sub(r"^a ", "", s)
    dot = "with a dot" in s
    s = s.replace("with a dot", "").strip()
    size = "small" if "small" in s else ("large" if "large" in s else None)
    colour = None
    for c in ("red", "blue", "green"):
        if c in s:
            colour = c
            break
    shape = None
    for sh in ("triangle", "square", "circle", "pentagon", "hexagon"):
        if sh in s:
            shape = sh
            break
    return {"shape": shape, "colour": colour, "size": size, "dot": dot}


def _figure_prims(cx, cy, fig):
    if fig is None:
        return [text(cx, cy, "?", size=34, fill=RED)]
    shp = fig.get("shape")
    col = fig.get("colour") or "gray"
    size = fig.get("size")
    r = 16 if size == "small" else (30 if size == "large" else 24)
    fill = COLORS.get(col, GRAY)
    if shp == "triangle":
        prims = [reg_poly(cx, cy, r, 3, -90, fill)]
    elif shp == "square":
        prims = [reg_poly(cx, cy, r, 4, 0, fill)]
    elif shp == "pentagon":
        prims = [reg_poly(cx, cy, r, 5, -90, fill)]
    elif shp == "hexagon":
        prims = [reg_poly(cx, cy, r, 6, 0, fill)]
    else:
        prims = [circle(cx, cy, r, fill)]
    if fig.get("dot"):
        prims.append(circle(cx, cy, 5, DARK))
    return prims


def odd_one_out_layout(spec):
    prims = []
    items = spec.get("items", [])
    prims.append(text(180, 24, "Odd one out", size=16))
    n = len(items)
    xs = [55 + i * (250 / max(n - 1, 1)) for i in range(n)]
    for i, it in enumerate(items):
        prims += _figure_prims(xs[i], 120, _parse_fig(it.get("desc")))
        prims.append(text(xs[i], 185, it.get("id"), size=14, fill=DARK))
    return prims, 360, 262


def shape_analogy_layout(spec):
    prims = []
    rule = spec.get("rule", "")
    p1 = spec.get("pair1", {})
    p2 = spec.get("pair2", {})
    prims.append(text(180, 22, "Figure analogy: " + str(rule), size=13))

    def draw_pair(kv, x, y):
        out = []
        for k, v in kv.items():
            out += _figure_prims(x, y, _parse_fig(k))
            out.append(text(x + 35, y + 40, "->", size=18, fill=DARK))
            if v == "?":
                out.append(text(x + 70, y, "?", size=34, fill=RED))
            else:
                out += _figure_prims(x + 70, y, _parse_fig(v))
            break
        return out
    prims += draw_pair(p1, 70, 120)
    prims += draw_pair(p2, 70, 190)
    return prims, 360, 262


def count_sequence_layout(spec):
    prims = []
    counts = spec.get("counts", [])
    nxt = spec.get("next")
    prims.append(text(180, 22, "Count sequence (dots)", size=15))
    allc = list(counts) + ([nxt] if nxt is not None else [])
    n = len(allc)
    xs = [40 + i * (280 / max(n - 1, 1)) for i in range(n)]
    for i, c in enumerate(allc):
        draw_n = min(c, 8)
        prims += dots(xs[i], 130, draw_n, spread=9, r=5)
        if c > 8:
            prims.append(text(xs[i], 130, "...", size=14, fill=DARK))
        prims.append(text(xs[i], 170, str(c), size=14, fill=DARK))
        if i < n - 1:
            prims.append(text((xs[i] + xs[i + 1]) / 2, 130, "->", size=16, fill=GRAY))
    if nxt is not None:
        prims.append(text(xs[-1], 195, "next", size=12, fill=RED))
    return prims, 360, 262


def _draw_cell_value(val, cx, cy):
    out = []
    if val is None or str(val).strip() == "?":
        out.append(text(cx, cy, "?", size=34, fill=RED))
        return out
    s = str(val)
    m = re.match(r"(\w+)\s+circle\s+(\d)", s)
    if m:
        col = m.group(1)
        d = int(m.group(2))
        out.append(circle(cx, cy, 26, COLORS.get(col, WHITE)))
        out += dots(cx, cy, d, spread=14, r=4)
        return out
    if "circle+dot" in s:
        out.append(circle(cx, cy, 26, WHITE))
        out.append(circle(cx, cy, 5, DARK))
        return out
    fig = _parse_fig(s)
    if fig and fig.get("shape"):
        return _figure_prims(cx, cy, fig)
    out.append(text(cx, cy, s, size=14, fill=DARK))
    return out


def matrix_layout(spec, rows, cols):
    prims = []
    cells = spec.get("cells", [])
    prims.append(text(180, 20, str(rows) + "x" + str(cols) + " matrix", size=15))
    cw, ch = 70, 70
    gx, gy = 180 - cols * cw / 2, 45
    for r in range(rows):
        for c in range(cols):
            val = cells[r][c]
            x = gx + c * cw
            y = gy + r * ch
            prims.append(rect(x, y, cw - 10, ch - 10, WHITE, rx=6))
            prims += _draw_cell_value(val, x + (cw - 10) / 2, y + (ch - 10) / 2)
    return prims, 360, 262


def rotation_transform_sequence_layout(spec):
    prims = []
    rules = spec.get("rules", [])
    steps = [spec.get("step1"), spec.get("step2"), spec.get("step3"), spec.get("step4")]
    steps = [s for s in steps if s]
    prims.append(text(180, 20, "Integrated: " + " + ".join(rules), size=13))
    n = len(steps)
    xs = [55 + i * (250 / max(n - 1, 1)) for i in range(n)]
    for i, s in enumerate(steps):
        m = re.match(r"(\w+)\s+(\w+)\s+(\d+)", s)
        if not m:
            continue
        shp, dirn, sides = m.group(1), m.group(2), int(m.group(3))
        dd = {"up": -90, "right": 0, "down": 90, "left": 180}[dirn]
        prims.append(reg_poly(xs[i], 120, 32, sides, dd, BLUE if i % 2 == 0 else RED))
        prims.append(text(xs[i], 175, s, size=12, fill=GRAY))
        if i < n - 1:
            prims.append(text((xs[i] + xs[i + 1]) / 2, 120, "->", size=18, fill=DARK))
    return prims, 360, 262


def layout_for(spec, id, level):
    spec = dict(spec)
    spec["_id"] = id
    spec["_level"] = level
    t = spec.get("type")
    if t == "single_rotation":
        return L_layout(spec)
    if t == "rotation_sequence":
        return rotation_sequence_layout(spec)
    if t == "reflection":
        return reflection_layout(spec)
    if t == "cube_faces":
        return cube_faces_layout(spec)
    if t == "cube_net":
        return cube_net_layout(spec)
    if t == "rotation_3d":
        return rotation_3d_layout(spec)
    if t == "shape_transformation":
        return shape_transformation_layout(spec)
    if t == "combine_shapes":
        return combine_shapes_layout(spec)
    if t == "odd_one_out":
        return odd_one_out_layout(spec)
    if t in ("shape_analogy", "shape_animation"):
        return shape_analogy_layout(spec)
    if t == "count_sequence":
        return count_sequence_layout(spec)
    if t == "analogy_matrix":
        return matrix_layout(spec, 2, 2)
    if t == "matrix_3x3":
        return matrix_layout(spec, 3, 3)
    if t == "rotation_transform_sequence":
        return rotation_transform_sequence_layout(spec)
    return [text(180, 130, "NO RENDERER FOR: " + str(t), size=16, fill=RED)], 360, 262


def to_png(prims, w, h, path):
    img = Image.new("RGBA", (w, h), BG)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
    for p in prims:
        t = p["t"]
        if t == "circle":
            d.ellipse([p["cx"] - p["r"], p["cy"] - p["r"], p["cx"] + p["r"], p["cy"] + p["r"]],
                      fill=p["fill"], outline=p["stroke"], width=p.get("sw", SW))
        elif t == "poly":
            d.polygon([(int(round(a)), int(round(b))) for a, b in p["points"]], fill=p["fill"], outline=p["stroke"])
        elif t == "rect":
            d.rounded_rectangle([p["x"], p["y"], p["x"] + p["w"], p["y"] + p["h"]],
                                radius=p.get("rx", 8), fill=p["fill"], outline=p["stroke"], width=p.get("sw", SW))
        elif t == "line":
            d.line([p["x1"], p["y1"], p["x2"], p["y2"]], fill=p["stroke"], width=p.get("sw", SW))
        elif t == "arc":
            d.arc([p["cx"] - p["r"], p["cy"] - p["r"], p["cx"] + p["r"], p["cy"] + p["r"]],
                  int(p["a0"]), int(p["a1"]), fill=p["stroke"], width=p.get("sw", SW))
        elif t == "text":
            f = font
            if p.get("size"):
                try:
                    f = ImageFont.truetype("arial.ttf", p["size"])
                except Exception:
                    f = font
            anchor = p.get("anchor", "middle")
            pil_anchor = "mm" if anchor == "middle" else ("lm" if anchor == "start" else "rm")
            d.text((p["x"], p["y"]), p["s"], font=f, fill=p["fill"], anchor=pil_anchor)
    img.convert("RGB").save(path)


def to_svg(prims, w, h, path):
    out = ['<?xml version="1.0" encoding="UTF-8"?>']
    out.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (w, h, w, h))
    out.append('<rect width="%d" height="%d" fill="%s"/>' % (w, h, BG))
    for p in prims:
        t = p["t"]
        if t == "circle":
            out.append('<circle cx="%g" cy="%g" r="%g" fill="%s" stroke="%s" stroke-width="%g"/>' %
                       (p["cx"], p["cy"], p["r"], p["fill"], p["stroke"], p.get("sw", SW)))
        elif t == "poly":
            pts = " ".join("%g,%g" % (pt[0], pt[1]) for pt in p["points"])
            out.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%g"/>' %
                       (pts, p["fill"], p["stroke"], p.get("sw", SW)))
        elif t == "rect":
            out.append('<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="%s" stroke="%s" stroke-width="%g"/>' %
                       (p["x"], p["y"], p["w"], p["h"], p.get("rx", 8), p["fill"], p["stroke"], p.get("sw", SW)))
        elif t == "line":
            out.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="%g"/>' %
                       (p["x1"], p["y1"], p["x2"], p["y2"], p["stroke"], p.get("sw", SW)))
        elif t == "arc":
            a0, a1 = math.radians(p["a0"]), math.radians(p["a1"])
            n = 24
            pts = []
            for i in range(n + 1):
                a = a0 + (a1 - a0) * i / n
                pts.append((p["cx"] + p["r"] * math.cos(a), p["cy"] + p["r"] * math.sin(a)))
            pstr = " ".join("%g,%g" % pt for pt in pts)
            out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%g"/>' %
                       (pstr, p["stroke"], p.get("sw", SW)))
        elif t == "text":
            out.append('<text x="%g" y="%g" font-size="%g" fill="%s" text-anchor="%s" font-family="sans-serif" font-weight="%s">%s</text>' %
                       (p["x"], p["y"], p["size"], p["fill"], p.get("anchor", "middle"), p.get("weight", "bold"),
                        _esc(p["s"])))
    out.append('</svg>')
    with open(path, "w") as f:
        f.write("\n".join(out))


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_all(json_path, out_dir):
    with open(json_path) as f:
        j = json.load(f)
    os.makedirs(out_dir, exist_ok=True)
    count = 0
    for q in j["questions"]:
        spec = q.get("visual_spec")
        if not (q.get("visual_required") and spec):
            continue
        prims, w, h = layout_for(spec, q["id"], q.get("level", ""))
        base = os.path.join(out_dir, q["id"])
        to_png(prims, w, h, base + ".png")
        to_svg(prims, w, h, base + ".svg")
        count += 1
    print("rendered", count, "visual questions to", out_dir)


if __name__ == "__main__":
    jp = sys.argv[1] if len(sys.argv) > 1 else r"C:\Projects\brainactive-android\revamp\pilot\brainactive_p3_high_ability_pilot.json"
    od = sys.argv[2] if len(sys.argv) > 2 else r"C:\Projects\brainactive-android\revamp\renderer\output"
    render_all(jp, od)
