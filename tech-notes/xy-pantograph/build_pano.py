#!/usr/bin/env python3
"""Generate readable SVG figures for the XY pantograph note."""
import math
from pathlib import Path

OUT = Path(__file__).parent
FONT = "Liberation Sans"

PAPER = "#f6f3ea"
INK = "#241c16"
MUTED = "#6b6258"
LINE = "#2a241e"
PROX = "#1e4d7b"
DIST = "#1f6b4a"
BELT = "#d85a12"
BEAR = "#2456c4"
HEAD = "#8c3b14"
DIM = "#9a3412"
GHOST = "#8b939c"
STEEL = "#5c6770"
PLATE = "#e4dccf"


def esc(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def svg_open(w, h):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<rect width="100%" height="100%" fill="{PAPER}"/>
<style>
  text {{ font-family: "{FONT}", sans-serif; fill: {INK}; }}
  .title {{ font-size: 22px; font-weight: 700; }}
  .sub {{ font-size: 13px; fill: {MUTED}; }}
  .lab {{ font-size: 14px; font-weight: 700; }}
  .sm {{ font-size: 12px; fill: #3c342c; }}
  .dim {{ font-size: 12px; fill: {DIM}; font-weight: 700; }}
  .halo {{ stroke: {PAPER}; stroke-width: 4px; paint-order: stroke fill; }}
</style>
<defs>
  <marker id="ah" viewBox="0 0 10 8" refX="9" refY="4" markerWidth="8" markerHeight="6" orient="auto">
    <path d="M0,0 L10,4 L0,8 Z" fill="{BELT}"/>
  </marker>
  <marker id="ad" viewBox="0 0 10 8" refX="9" refY="4" markerWidth="8" markerHeight="6" orient="auto">
    <path d="M0,0 L10,4 L0,8 Z" fill="{DIM}"/>
  </marker>
  <pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(40)">
    <line x1="0" y1="0" x2="0" y2="7" stroke="#b7ad9e" stroke-width="1.2"/>
  </pattern>
  <pattern id="hatch2" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(40)">
    <line x1="0" y1="0" x2="0" y2="6" stroke="#9aa3ad" stroke-width="1"/>
  </pattern>
</defs>
'''


def title(parts, text, sub, w):
    parts.append(f'<text class="title" x="28" y="36">{esc(text)}</text>')
    parts.append(f'<text class="sub" x="28" y="58">{esc(sub)}</text>')
    parts.append(f'<line x1="28" y1="70" x2="{w-28}" y2="70" stroke="#e0d6c6" stroke-width="1"/>')


def dim_h(parts, x1, x2, y, text, above=True):
    parts.append(
        f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="{DIM}" stroke-width="1.1" marker-end="url(#ad)"/>'
    )
    parts.append(
        f'<line x1="{x2:.1f}" y1="{y:.1f}" x2="{x1:.1f}" y2="{y:.1f}" stroke="{DIM}" stroke-width="1.1" marker-end="url(#ad)"/>'
    )
    ty = y - 6 if above else y + 15
    parts.append(
        f'<text class="dim halo" x="{(x1+x2)/2:.1f}" y="{ty:.1f}" text-anchor="middle">{esc(text)}</text>'
    )


def dim_v(parts, x, y1, y2, text, right=True):
    parts.append(
        f'<line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke="{DIM}" stroke-width="1.1" marker-end="url(#ad)"/>'
    )
    parts.append(
        f'<line x1="{x:.1f}" y1="{y2:.1f}" x2="{x:.1f}" y2="{y1:.1f}" stroke="{DIM}" stroke-width="1.1" marker-end="url(#ad)"/>'
    )
    tx = x + 8 if right else x - 8
    anchor = "start" if right else "end"
    parts.append(
        f'<text class="dim halo" x="{tx:.1f}" y="{(y1+y2)/2:.1f}" text-anchor="{anchor}" dominant-baseline="middle">{esc(text)}</text>'
    )


def tangents(c1, r1, c2, r2, internal=False):
    x1, y1 = c1
    x2, y2 = c2
    d = math.hypot(x2 - x1, y2 - y1)
    vx, vy = (x2 - x1) / d, (y2 - y1) / d
    rr = -r2 if internal else r2
    c = (r1 - rr) / d
    if abs(c) > 1:
        return []
    h = math.sqrt(max(0.0, 1 - c * c))
    res = []
    for sign in (1, -1):
        nx = vx * c - sign * h * vy
        ny = vy * c + sign * h * vx
        p1 = (x1 + r1 * nx, y1 + r1 * ny)
        p2 = (x2 + rr * nx, y2 + rr * ny)
        res.append((p1, p2))
    return res


def arc_cmd(c, r, p0, p1, cw):
    a0 = math.atan2(p0[1] - c[1], p0[0] - c[0])
    a1 = math.atan2(p1[1] - c[1], p1[0] - c[0])
    if cw:
        d = (a1 - a0) % (2 * math.pi)
    else:
        d = (a0 - a1) % (2 * math.pi)
    large = 1 if d > math.pi else 0
    sweep = 1 if cw else 0
    return f"A {r:.2f} {r:.2f} 0 {large} {sweep} {p1[0]:.2f} {p1[1]:.2f}", d


def rot_arrow(parts, cx, cy, r, a0_deg, sweep_deg, color):
    """Small rotation arrow. sweep_deg > 0 means clockwise on screen."""
    a0 = math.radians(a0_deg)
    a1 = math.radians(a0_deg + sweep_deg)
    p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
    p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
    large = 1 if abs(sweep_deg) > 180 else 0
    sweep = 1 if sweep_deg > 0 else 0
    parts.append(
        f'<path d="M {p0[0]:.1f} {p0[1]:.1f} A {r:.1f} {r:.1f} 0 {large} {sweep} {p1[0]:.1f} {p1[1]:.1f}" '
        f'fill="none" stroke="{color}" stroke-width="2.2" marker-end="url(#ah)"/>'
    )


def pulley(parts, c, r, label, sub=None):
    cx, cy = c
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" stroke="{LINE}" stroke-width="2.4"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r-7}" fill="none" stroke="#d7d0c4" stroke-width="1"/>')
    # tooth ticks
    for i in range(16):
        a = i * math.tau / 16
        x1 = cx + (r - 7) * math.cos(a)
        y1 = cy + (r - 7) * math.sin(a)
        x2 = cx + (r - 1.5) * math.cos(a)
        y2 = cy + (r - 1.5) * math.sin(a)
        parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{LINE}" stroke-width="1.4"/>'
        )
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="5" fill="{BEAR}"/>')
    parts.append(
        f'<text class="lab halo" x="{cx}" y="{cy-8}" text-anchor="middle">{esc(label)}</text>'
    )
    if sub:
        parts.append(
            f'<text class="sm halo" x="{cx}" y="{cy+12}" text-anchor="middle">{esc(sub)}</text>'
        )


def save(name, parts, w, h):
    text = svg_open(w, h) + "\n".join(parts) + "\n</svg>\n"
    (OUT / name).write_text(text, encoding="utf-8")
    print("wrote", name)


# ---------------------------------------------------------------------------
# 1. Kinematics
# ---------------------------------------------------------------------------

def fig_kinematics():
    w, h = 1120, 820
    parts = []
    title(
        parts,
        "Как рука едет по прямой",
        "Вид сверху. Рабочее положение α = 40°. Бледные контуры — края хода, 22° и 68°.",
        w,
    )
    L, half, k = 500.0, 90.0, 0.44
    ox, oy = 168, 455

    def S(x, y):
        return (ox + x * k, oy + y * k)

    def pose(deg):
        a = math.radians(deg)
        ex = L * math.cos(a)
        ey = half + L * math.sin(a)
        hx = 2 * L * math.cos(a)
        return dict(
            sa=S(0, -half),
            sb=S(0, half),
            ea=S(ex, -ey),
            eb=S(ex, ey),
            ha=S(hx, -half),
            hb=S(hx, half),
            hx=hx,
            deg=deg,
        )

    # portal rail
    parts.append(
        f'<rect x="36" y="250" width="46" height="410" fill="url(#hatch2)" stroke="{STEEL}" stroke-width="1.4"/>'
    )
    parts.append(
        '<text class="sm" transform="translate(58,455) rotate(-90)" text-anchor="middle">направляющая Y</text>'
    )

    # centerline, stopped before the nearest head so the label has a clear gap
    p0, p1 = S(-20, 0), S(300, 0)
    parts.append(
        f'<line x1="{p0[0]:.1f}" y1="{p0[1]:.1f}" x2="{p1[0]:.1f}" y2="{p1[1]:.1f}" stroke="#c4b8a4" stroke-width="1.2" stroke-dasharray="5 5"/>'
    )
    parts.append(
        f'<text class="sm halo" x="{p1[0]+8:.1f}" y="{p1[1]-8:.1f}">ось X</text>'
    )

    def arm(p, color, width, dash=None, opacity=1):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        for a, b in ((p["sa"], p["ea"]), (p["ea"], p["ha"]), (p["sb"], p["eb"]), (p["eb"], p["hb"])):
            parts.append(
                f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" opacity="{opacity}"{extra}/>'
            )

    def head(p, fill, stroke, sw=2):
        x = p["ha"][0]
        y1, y2 = p["ha"][1], p["hb"][1]
        parts.append(
            f'<rect x="{x:.1f}" y="{y1:.1f}" width="18" height="{y2-y1:.1f}" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
        )

    # ghosts
    for deg, tag in ((22, "22° · 927 мм"), (68, "68° · 375 мм")):
        p = pose(deg)
        arm(p, GHOST, 2.2, "7 6", 0.95)
        head(p, "#e7e1d6", GHOST, 1.4)
        parts.append(f'<circle cx="{p["ea"][0]:.1f}" cy="{p["ea"][1]:.1f}" r="3.5" fill="{GHOST}"/>')
        parts.append(f'<circle cx="{p["eb"][0]:.1f}" cy="{p["eb"][1]:.1f}" r="3.5" fill="{GHOST}"/>')

    p22, p68 = pose(22), pose(68)
    parts.append(
        f'<text class="sm halo" x="{p22["ha"][0]+22:.1f}" y="{p22["ha"][1]-6:.1f}">22° · 927 мм</text>'
    )
    parts.append(
        f'<text class="sm halo" x="{p68["ha"][0]+22:.1f}" y="{p68["hb"][1]+22:.1f}">68° · 375 мм</text>'
    )

    # working
    p = pose(40)
    # proximal then distal, so color split
    for a, b in ((p["sa"], p["ea"]), (p["sb"], p["eb"])):
        parts.append(
            f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{PROX}" stroke-width="7" stroke-linecap="round"/>'
        )
    for a, b in ((p["ea"], p["ha"]), (p["eb"], p["hb"])):
        parts.append(
            f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{DIST}" stroke-width="7" stroke-linecap="round"/>'
        )
    head(p, "#f3d2c4", HEAD, 2)
    for key in ("ea", "eb"):
        parts.append(
            f'<circle cx="{p[key][0]:.1f}" cy="{p[key][1]:.1f}" r="6" fill="#fff" stroke="{HEAD}" stroke-width="2.4"/>'
        )
    for key in ("sa", "sb"):
        parts.append(f'<circle cx="{p[key][0]:.1f}" cy="{p[key][1]:.1f}" r="7" fill="{BEAR}"/>')

    # carriage sits behind the shafts; arms leave the front edge cleanly
    parts.append(
        f'<rect x="86" y="400" width="76" height="128" rx="4" fill="{PLATE}" stroke="{LINE}" stroke-width="1.8"/>'
    )
    parts.append('<text class="sm" x="124" y="458" text-anchor="middle">каретка</text>')
    parts.append('<text class="sm" x="124" y="474" text-anchor="middle">плиты 8 мм</text>')
    for key, name, dy in (("sa", "вал А", -14), ("sb", "вал Б", 18)):
        parts.append(f'<circle cx="{p[key][0]:.1f}" cy="{p[key][1]:.1f}" r="7" fill="{BEAR}"/>')
        parts.append(
            f'<text class="sm halo" x="{p[key][0]+12:.1f}" y="{p[key][1]+dy:.1f}">{name}</text>'
        )

    # labels on working arms
    def mid(a, b, t=0.45):
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

    m = mid(p["sa"], p["ea"], 0.42)
    parts.append(f'<text class="lab halo" x="{m[0]:.1f}" y="{m[1]-12:.1f}">плечо 1</text>')
    m = mid(p["sb"], p["eb"], 0.42)
    parts.append(f'<text class="lab halo" x="{m[0]:.1f}" y="{m[1]+20:.1f}">плечо 2</text>')
    m = mid(p["ea"], p["ha"], 0.5)
    parts.append(f'<text class="lab halo" x="{m[0]:.1f}" y="{m[1]-12:.1f}">плечо 3</text>')
    m = mid(p["eb"], p["hb"], 0.5)
    parts.append(f'<text class="lab halo" x="{m[0]:.1f}" y="{m[1]+20:.1f}">плечо 4</text>')
    parts.append(
        f'<text class="lab halo" x="{p["ea"][0]:.1f}" y="{p["ea"][1]-14:.1f}" text-anchor="middle">локоть</text>'
    )
    parts.append(
        f'<text class="lab halo" x="{p["ha"][0]+26:.1f}" y="{p["ha"][1]+8:.1f}">голова</text>'
    )
    parts.append(
        f'<text class="sm halo" x="{p["ha"][0]+26:.1f}" y="{p["ha"][1]+24:.1f}">40° · 766 мм</text>'
    )

    # angle arc at shaft A
    sa = p["sa"]
    # forward is +x; arm direction
    ang = math.atan2(p["ea"][1] - sa[1], p["ea"][0] - sa[0])
    r = 36
    p_forward = (sa[0] + r, sa[1])
    p_arm = (sa[0] + r * math.cos(ang), sa[1] + r * math.sin(ang))
    parts.append(
        f'<path d="M {p_forward[0]:.1f} {p_forward[1]:.1f} A {r} {r} 0 0 0 {p_arm[0]:.1f} {p_arm[1]:.1f}" fill="none" stroke="{DIM}" stroke-width="1.4"/>'
    )
    parts.append(f'<text class="dim halo" x="{sa[0]+44:.1f}" y="{sa[1]-28:.1f}">α</text>')
    parts.append('<text class="dim halo" x="124" y="508" text-anchor="middle">180 мм</text>')

    # legend
    lx, ly = 860, 100
    parts.append(
        f'<rect x="{lx}" y="{ly}" width="230" height="168" rx="8" fill="#fff" stroke="#e0d6c6"/>'
    )
    items = [
        (PROX, "плечи 1 и 2, у валов"),
        (DIST, "плечи 3 и 4, у головы"),
        (GHOST, "края хода"),
        (BEAR, "валы А и Б"),
    ]
    for i, (col, text) in enumerate(items):
        yy = ly + 28 + i * 34
        parts.append(
            f'<line x1="{lx+16}" y1="{yy}" x2="{lx+48}" y2="{yy}" stroke="{col}" stroke-width="6" stroke-linecap="round"/>'
        )
        parts.append(f'<text class="sm" x="{lx+58}" y="{yy+4}">{esc(text)}</text>')

    parts.append(
        '<text class="sm" x="28" y="792">Длины плеч равны, ширина головы равна расстоянию между валами — иначе голова уведёт вбок. x = 2·L·cos α.</text>'
    )
    save("01-kinematics.svg", parts, w, h)


# ---------------------------------------------------------------------------
# 2. Belts
# ---------------------------------------------------------------------------

def fig_belts():
    w, h = 1200, 860
    parts = []
    title(
        parts,
        "Два ремня вместо одной выворотной петли",
        "Верхняя плоскость зеркалит валы. Нижняя забирает момент с мотора. Оба ремня HTD5M, ширина 15 мм.",
        w,
    )

    # height stack
    parts.append('<text class="lab" x="28" y="96">Стопка на валу, сверху вниз</text>')
    blocks = [
        ("#d9e2ec", "уголок"),
        ("#c5d4f5", "UCF204"),
        ("#f6d2b8", "60T синхр."),
        ("#f6e0b8", "60T редукт."),
        ("#c5d4f5", "UCF204"),
        ("#d9e2ec", "уголок"),
        ("#d7e4c8", "мотор снизу"),
    ]
    x = 28
    for i, (col, name) in enumerate(blocks):
        parts.append(
            f'<rect x="{x}" y="108" width="118" height="36" rx="4" fill="{col}" stroke="{LINE}" stroke-width="1"/>'
        )
        parts.append(
            f'<text class="sm" x="{x+59}" y="130" text-anchor="middle">{esc(name)}</text>'
        )
        if i < len(blocks) - 1:
            parts.append(f'<text class="sm" x="{x+122}" y="130">›</text>')
        x += 132

    # ----- left: crossed sync, vertical line of centers (Y on the page) -----
    parts.append('<text class="lab" x="40" y="178">Верхняя плоскость · синхронизация 1:1</text>')
    A = (300.0, 250.0)
    B = (300.0, 560.0)
    R = 72.0
    segs = tangents(A, R, B, R, True)
    # segs: two internal tangents (pA, pB)
    # Identify upper/lower by y of point on A
    segs = sorted(segs, key=lambda s: s[0][1])
    # segs[0] touches A higher on the page (smaller y) 
    pulley(parts, A, R, "А", "60 зубьев")
    pulley(parts, B, R, "Б", "60 зубьев")

    def gap_line(p, q, gap=16):
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        a = (mx - ux * gap, my - uy * gap)
        b = (mx + ux * gap, my + uy * gap)
        parts.append(
            f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{a[0]:.1f}" y2="{a[1]:.1f}" stroke="{BELT}" stroke-width="6" stroke-linecap="butt"/>'
        )
        parts.append(
            f'<line x1="{b[0]:.1f}" y1="{b[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" stroke="{BELT}" stroke-width="6" stroke-linecap="butt"/>'
        )
        return (mx, my)

    mids = []
    for seg in segs:
        mids.append(gap_line(seg[0], seg[1]))

    # outer arcs. From each pulley's two tangent points, take the arc that bulges AWAY
    # from the partner (the major arc).
    def outer_arc(c, partner, r, pts):
        # pts are the two tangent points on this circle
        p0, p1 = pts
        # test both directions; pick the one whose midpoint is farther from partner
        best = None
        for cw in (True, False):
            cmd, d = arc_cmd(c, r, p0, p1, cw)
            # midpoint angle
            a0 = math.atan2(p0[1] - c[1], p0[0] - c[0])
            if cw:
                amid = a0 + d / 2
            else:
                amid = a0 - d / 2
            mx = c[0] + r * math.cos(amid)
            my = c[1] + r * math.sin(amid)
            dist = math.hypot(mx - partner[0], my - partner[1])
            if best is None or dist > best[0]:
                best = (dist, cmd, d, cw, (mx, my))
        return best

    ptsA = [segs[0][0], segs[1][0]]
    ptsB = [segs[0][1], segs[1][1]]
    arcA = outer_arc(A, B, R, ptsA)
    arcB = outer_arc(B, A, R, ptsB)
    parts.append(
        f'<path d="M {ptsA[0][0]:.2f} {ptsA[0][1]:.2f} {arcA[1]}" fill="none" stroke="{BELT}" stroke-width="6"/>'
    )
    parts.append(
        f'<path d="M {ptsB[0][0]:.2f} {ptsB[0][1]:.2f} {arcB[1]}" fill="none" stroke="{BELT}" stroke-width="6"/>'
    )

    # shoe at cross — both mids should be near the same point
    mx = sum(p[0] for p in mids) / 2
    my = sum(p[1] for p in mids) / 2
    parts.append(
        f'<rect x="{mx-16:.1f}" y="{my-10:.1f}" width="32" height="20" rx="3" fill="#fff" stroke="{LINE}" stroke-width="1.3"/>'
    )
    parts.append(
        f'<text class="sm halo" x="{mx+22:.1f}" y="{my-14:.1f}">башмак</text>'
    )
    parts.append(
        f'<text class="sm halo" x="{mx+22:.1f}" y="{my+2:.1f}">зазор 1–2 мм</text>'
    )

    # rotation arrows inside, after we know outer direction.
    # Belt on A's outer arc: sample travel. We don't know path direction.
    # Draw explicit arrows: A clockwise, B counterclockwise — verified for this cross
    # when the belt runs up the outer side of A.
    rot_arrow(parts, A[0], A[1], 40, 200, 80, BELT)
    rot_arrow(parts, B[0], B[1], 40, -20, -80, BELT)
    parts.append(f'<text class="sm halo" x="{A[0]+78:.1f}" y="{A[1]-40:.1f}">по часовой</text>')
    parts.append(f'<text class="sm halo" x="{B[0]+78:.1f}" y="{B[1]+48:.1f}">против</text>')

    # tensioner on the outer (left) flank, clear of the stack above
    ten = (A[0] - R - 36, A[1])
    parts.append(
        f'<circle cx="{ten[0]:.1f}" cy="{ten[1]:.1f}" r="14" fill="#fff" stroke="{STEEL}" stroke-width="2"/>'
    )
    parts.append(
        f'<circle cx="{ten[0]:.1f}" cy="{ten[1]:.1f}" r="8" fill="none" stroke="{STEEL}" stroke-width="1"/>'
    )
    parts.append(
        f'<text class="sm" x="{ten[0]-20:.1f}" y="{ten[1]-2:.1f}" text-anchor="end">натяжитель</text>'
    )
    parts.append(
        f'<text class="sm" x="{ten[0]-20:.1f}" y="{ten[1]+14:.1f}" text-anchor="end">тыльная сторона</text>'
    )

    # stubs of arms to the right, matching kinematics colors
    parts.append(
        f'<line x1="{A[0]+R:.1f}" y1="{A[1]:.1f}" x2="{A[0]+R+54:.1f}" y2="{A[1]-28:.1f}" stroke="{PROX}" stroke-width="6" stroke-linecap="round"/>'
    )
    parts.append(
        f'<line x1="{B[0]+R:.1f}" y1="{B[1]:.1f}" x2="{B[0]+R+54:.1f}" y2="{B[1]+28:.1f}" stroke="{PROX}" stroke-width="6" stroke-linecap="round"/>'
    )
    parts.append(f'<text class="sm" x="{A[0]+R+60:.1f}" y="{A[1]-24:.1f}">к плечу 1</text>')
    parts.append(f'<text class="sm" x="{B[0]+R+60:.1f}" y="{B[1]+36:.1f}">к плечу 2</text>')
    parts.append('<text class="sm" x="40" y="640">X, к голове →</text>')
    parts.append('<text class="sm" x="40" y="658">← к порталу</text>')

    # ----- right: reduction plane -----
    parts.append('<text class="lab" x="760" y="178">Нижняя плоскость · редукция 3:1</text>')
    SA = (980.0, 400.0)
    MO = (760.0, 400.0)
    rS, rM = 70.0, 24.0
    pulley(parts, SA, rS, "А", "60 зубьев")
    # motor pulley without pretending it is 60T
    parts.append(f'<circle cx="{MO[0]}" cy="{MO[1]}" r="{rM}" fill="#fff" stroke="{LINE}" stroke-width="2.4"/>')
    for i in range(10):
        a = i * math.tau / 10
        x1 = MO[0] + (rM - 6) * math.cos(a)
        y1 = MO[1] + (rM - 6) * math.sin(a)
        x2 = MO[0] + (rM - 1.2) * math.cos(a)
        y2 = MO[1] + (rM - 1.2) * math.sin(a)
        parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{LINE}" stroke-width="1.3"/>'
        )
    parts.append(f'<circle cx="{MO[0]}" cy="{MO[1]}" r="3.5" fill="#3f6212"/>')
    parts.append(f'<text class="lab halo" x="{MO[0]}" y="{MO[1]-36}" text-anchor="middle">20T</text>')

    ext = tangents(MO, rM, SA, rS, False)
    # open belt: two external spans + outer arcs
    # draw both spans
    for p, q in ext:
        parts.append(
            f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" stroke="{BELT}" stroke-width="6" stroke-linecap="round"/>'
        )
    # arcs: for each circle, between its two tangent points, choose the arc farther from the other center
    ptsM = [ext[0][0], ext[1][0]]
    ptsS = [ext[0][1], ext[1][1]]
    aM = outer_arc(MO, SA, rM, ptsM)
    aS = outer_arc(SA, MO, rS, ptsS)
    parts.append(
        f'<path d="M {ptsM[0][0]:.2f} {ptsM[0][1]:.2f} {aM[1]}" fill="none" stroke="{BELT}" stroke-width="6"/>'
    )
    parts.append(
        f'<path d="M {ptsS[0][0]:.2f} {ptsS[0][1]:.2f} {aS[1]}" fill="none" stroke="{BELT}" stroke-width="6"/>'
    )
    # redraw pulley centers on top of belt
    parts.append(f'<circle cx="{SA[0]}" cy="{SA[1]}" r="5" fill="{BEAR}"/>')
    parts.append(f'<circle cx="{MO[0]}" cy="{MO[1]}" r="3.5" fill="#3f6212"/>')

    # motor body square and slots
    parts.append(
        f'<rect x="{MO[0]-46}" y="{MO[1]+40}" width="92" height="70" rx="4" fill="#e7f0d4" stroke="{LINE}" stroke-width="1.4"/>'
    )
    parts.append(
        f'<text class="sm" x="{MO[0]}" y="{MO[1]+72}" text-anchor="middle">NEMA 23</text>'
    )
    parts.append(
        f'<text class="sm" x="{MO[0]}" y="{MO[1]+90}" text-anchor="middle">под нижней плитой</text>'
    )
    # slot arrows
    parts.append(
        f'<line x1="{MO[0]-70}" y1="{MO[1]}" x2="{MO[0]-52}" y2="{MO[1]}" stroke="{DIM}" stroke-width="1.4" marker-end="url(#ad)"/>'
    )
    parts.append(
        f'<text class="dim halo" x="{MO[0]-74}" y="{MO[1]-10}" text-anchor="end">натяг</text>'
    )
    parts.append(
        f'<text class="sm" x="{SA[0]+80}" y="{SA[1]-8}">тот же вал А</text>'
    )
    parts.append(
        f'<text class="sm" x="{SA[0]+80}" y="{SA[1]+12}">шкив ниже синхронного</text>'
    )
    parts.append(
        '<text class="sm" x="760" y="640">Оба шкива крутятся в одну сторону.</text>'
    )
    parts.append(
        '<text class="sm" x="760" y="658">Момент на валу ×3, люфта шестерён нет.</text>'
    )

    parts.append(
        '<text class="sm" x="28" y="830">Перекрест нужен один раз и только между равными шкивами. Мотор в эту петлю не ставится: у шкива 20 зубьев не набирается обхват.</text>'
    )
    save("02-belts.svg", parts, w, h)


# ---------------------------------------------------------------------------
# 3. Side truss
# ---------------------------------------------------------------------------

def fig_side():
    w, h = 1180, 640
    parts = []
    title(
        parts,
        "Ферма держит вес, ремень держит поворот",
        "Вид сбоку, один борт. Второе плечо — зеркало и на этом виде закрыто первым. Масштаб единый.",
        w,
    )
    k = 0.78
    # x_mm from rear face of carriage; z_mm from lower chord upward
    def X(xmm):
        return 36 + xmm * k
    def Y(zmm):
        return 430 - zmm * k

    # portal
    parts.append(
        f'<rect x="24" y="{Y(300):.1f}" width="36" height="{300*k:.1f}" fill="url(#hatch2)" stroke="{STEEL}"/>'
    )
    parts.append(
        f'<text class="sm" transform="translate(40,{Y(150):.1f}) rotate(-90)" text-anchor="middle">каретка Y</text>'
    )

    # carriage plates
    z_bear_hi, z_bear_lo = 200, 40
    # plates 8 mm on the outer side of each bearing center, schematic
    def plate(z_top, label_y_off=0):
        y = Y(z_top)
        parts.append(
            f'<rect x="{X(20):.1f}" y="{y:.1f}" width="{160*k:.1f}" height="{8*k:.1f}" fill="url(#hatch)" stroke="{LINE}" stroke-width="1"/>'
        )

    # upper plate just above upper bearing, lower plate just below lower bearing
    plate_hi_top = z_bear_hi + 16
    plate_lo_top = z_bear_lo - 16 - 8
    plate(plate_hi_top)
    plate(plate_lo_top)
    # side cheek closing the box
    parts.append(
        f'<rect x="{X(20):.1f}" y="{Y(plate_hi_top+8):.1f}" width="{8*k:.1f}" height="{(plate_hi_top+8-plate_lo_top)*k:.1f}" fill="{PLATE}" stroke="{LINE}" stroke-width="1"/>'
    )

    # bearings
    for z, name in ((z_bear_hi, "UCF204"), (z_bear_lo, "UCF204")):
        cx, cy = X(150), Y(z)
        parts.append(
            f'<rect x="{cx-16:.1f}" y="{cy-12:.1f}" width="32" height="24" rx="2" fill="#d5e1f8" stroke="{BEAR}" stroke-width="1.4"/>'
        )
        parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="{BEAR}"/>')

    # shaft between bearings
    parts.append(
        f'<line x1="{X(150):.1f}" y1="{Y(z_bear_hi):.1f}" x2="{X(150):.1f}" y2="{Y(z_bear_lo):.1f}" stroke="{STEEL}" stroke-width="6" stroke-linecap="round"/>'
    )

    # chords
    x_shaft, x_elbow, x_head = 150, 650, 1150
    for z, col in ((240, PROX), (0, PROX)):
        parts.append(
            f'<line x1="{X(x_shaft):.1f}" y1="{Y(z):.1f}" x2="{X(x_elbow):.1f}" y2="{Y(z):.1f}" stroke="{col}" stroke-width="7" stroke-linecap="round"/>'
        )
    for z in (240, 0):
        parts.append(
            f'<line x1="{X(x_elbow):.1f}" y1="{Y(z):.1f}" x2="{X(x_head):.1f}" y2="{Y(z):.1f}" stroke="{DIST}" stroke-width="7" stroke-linecap="round"/>'
        )

    # diagonals, 3 bays proximal, 3 distal
    def zigzag(x0, x1, z0, z1, n, color):
        xs = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
        for i in range(n):
            z_a = z0 if i % 2 == 0 else z1
            z_b = z1 if i % 2 == 0 else z0
            parts.append(
                f'<line x1="{X(xs[i]):.1f}" y1="{Y(z_a):.1f}" x2="{X(xs[i+1]):.1f}" y2="{Y(z_b):.1f}" stroke="{color}" stroke-width="2.4"/>'
            )

    zigzag(170, 630, 0, 240, 3, "#7d8790")
    zigzag(670, 1130, 240, 0, 3, "#7d8790")

    # elbow box
    parts.append(
        f'<rect x="{X(632):.1f}" y="{Y(252):.1f}" width="{36*k:.1f}" height="{(252)*k:.1f}" rx="2" fill="#fff" stroke="{HEAD}" stroke-width="1.8"/>'
    )
    parts.append(
        f'<line x1="{X(650):.1f}" y1="{Y(248):.1f}" x2="{X(650):.1f}" y2="{Y(-8):.1f}" stroke="{HEAD}" stroke-width="2" stroke-dasharray="4 3"/>'
    )
    parts.append(
        f'<text class="lab halo" x="{X(650):.1f}" y="{Y(348):.1f}" text-anchor="middle">локоть, палец Ø12</text>'
    )

    # head
    parts.append(
        f'<rect x="{X(1135):.1f}" y="{Y(200):.1f}" width="{70*k:.1f}" height="{160*k:.1f}" rx="3" fill="#f3d2c4" stroke="{HEAD}" stroke-width="1.8"/>'
    )
    parts.append(
        f'<text class="lab" x="{X(1170):.1f}" y="{Y(130):.1f}" text-anchor="middle">голова</text>'
    )
    # tool
    parts.append(
        f'<rect x="{X(1160):.1f}" y="{Y(70):.1f}" width="{16*k:.1f}" height="{40*k:.1f}" fill="{HEAD}"/>'
    )
    parts.append(
        f'<line x1="{X(1170):.1f}" y1="{Y(60):.1f}" x2="{X(1170):.1f}" y2="{Y(20):.1f}" stroke="{DIM}" stroke-width="1.4" marker-end="url(#ad)"/>'
    )
    parts.append(
        f'<text class="dim halo" x="{X(1245):.1f}" y="{Y(48):.1f}">2 кг</text>'
    )

    # labels
    parts.append(
        f'<text class="lab halo" x="{X(260):.1f}" y="{Y(300):.1f}">плечо 1 · уголок 25×25×3</text>'
    )
    parts.append(
        f'<text class="sm halo" x="{X(260):.1f}" y="{Y(282):.1f}">полки наружу, раскосы 20×3</text>'
    )
    parts.append(
        f'<text class="lab halo" x="{X(900):.1f}" y="{Y(300):.1f}">плечо 3, та же ферма</text>'
    )

    # dimensions
    dim_h(parts, X(x_shaft), X(x_elbow), Y(-48), "500", above=False)
    dim_h(parts, X(x_elbow), X(x_head), Y(-48), "500", above=False)
    dim_v(parts, X(40), Y(240), Y(0), "240", right=False)
    dim_v(parts, X(210), Y(z_bear_hi), Y(z_bear_lo), "160", right=True)

    parts.append(
        f'<text class="sm halo" x="{X(78):.1f}" y="{Y(230):.1f}">UCF204</text>'
    )
    parts.append(
        '<text class="sm" x="48" y="610">Вес и провис замыкаются парой подшипников и поясами фермы. Ремень этого момента не видит — он только поворачивает валы.</text>'
    )
    save("03-side-truss.svg", parts, w, h)


# ---------------------------------------------------------------------------
# 4. Nodes
# ---------------------------------------------------------------------------

def panel(parts, x, y, w, h, heading):
    parts.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#fff" stroke="#e0d6c6"/>'
    )
    parts.append(f'<text class="lab" x="{x+16}" y="{y+26}">{esc(heading)}</text>')


def fig_nodes():
    w, h = 1200, 1040
    parts = []
    title(
        parts,
        "Узлы, которые собираются в гараже",
        "Плазма, токарный, сварка. Фрезеровка только лысок на валу и, по возможности, торца шипа.",
        w,
    )

    # ===== panel 1: shaft stack section =====
    panel(parts, 28, 88, 570, 450, "1 · Вал в каретке, разрез")
    sx = 250

    def box(x, y, bw, bh, fill, stroke=LINE):
        parts.append(
            f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="2" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>'
        )

    box(sx - 78, 128, 86, 14, "#d9e2ec")
    box(sx - 7, 142, 14, 28, "#c5ced6")
    box(sx - 110, 186, 250, 12, "url(#hatch)")
    box(sx - 26, 204, 52, 36, "#d5e1f8", BEAR)
    parts.append(f'<circle cx="{sx}" cy="222" r="5" fill="{BEAR}"/>')
    parts.append(
        f'<rect x="{sx-5}" y="204" width="10" height="200" fill="#b7c0c8" stroke="{STEEL}"/>'
    )
    box(sx - 70, 252, 140, 20, "#f6d2b8")
    box(sx - 70, 286, 140, 20, "#f6e0b8")
    parts.append(f'<circle cx="{sx}" cy="222" r="5" fill="{BEAR}"/>')
    parts.append(f'<circle cx="{sx}" cy="346" r="5" fill="{BEAR}"/>')
    box(sx - 26, 328, 52, 36, "#d5e1f8", BEAR)
    parts.append(f'<circle cx="{sx}" cy="346" r="5" fill="{BEAR}"/>')
    box(sx - 110, 372, 250, 12, "url(#hatch)")
    box(sx - 7, 384, 14, 28, "#c5ced6")
    box(sx - 78, 412, 86, 14, "#d9e2ec")
    # motor under the plate, rearward (to the left), pulley level with the reduction pulley
    box(90, 286, 36, 20, "#f6e0b8")
    parts.append('<line x1="108" y1="306" x2="108" y2="384" stroke="{0}" stroke-width="4"/>'.format(STEEL))
    box(78, 384, 60, 52, "#e7f0d4")
    parts.append(
        '<line x1="126" y1="292" x2="180" y2="292" stroke="{0}" stroke-width="3"/>'.format(BELT)
    )
    parts.append(
        '<line x1="126" y1="300" x2="180" y2="300" stroke="{0}" stroke-width="3"/>'.format(BELT)
    )
    parts.append(f'<circle cx="{sx}" cy="222" r="5" fill="{BEAR}"/>')
    parts.append(f'<circle cx="{sx}" cy="346" r="5" fill="{BEAR}"/>')
    parts.append(f'<text class="sm" x="{sx+78}" y="140">верхний уголок</text>')
    parts.append(f'<text class="sm" x="{sx+78}" y="162">шип</text>')
    parts.append(f'<text class="sm" x="{sx+148}" y="196">плита 8 мм</text>')
    parts.append(f'<text class="sm" x="{sx+36}" y="226">UCF204</text>')
    parts.append(f'<text class="sm" x="{sx+78}" y="266">60T синхронизация</text>')
    parts.append(f'<text class="sm" x="{sx+78}" y="300">60T редуктор</text>')
    parts.append(f'<text class="sm" x="{sx+36}" y="350">UCF204</text>')
    parts.append(f'<text class="sm" x="{sx+16}" y="424">нижний уголок</text>')
    parts.append('<text class="sm" x="78" y="458">NEMA 23</text>')
    parts.append('<text class="sm" x="78" y="474">под плитой</text>')
    dim_v(parts, 58, 222, 346, "160", right=False)
    parts.append('<text class="sm" x="48" y="516">Вал Ø20 Ст45, около 270 мм. Винты обоих UCF держат вал от осевого сдвига.</text>')

    # ===== panel 2: tang =====
    panel(parts, 614, 88, 558, 450, "2 · Шип вала и уголок")
    # side view
    parts.append('<text class="sm" x="636" y="140">Вид сбоку</text>')
    # Ø20 body, then a thinner tang with a fillet
    parts.append(
        f'<path d="M700,172 H812 V164 Q830,164 836,178 H910 V190 Q830,204 812,196 V196 H700 Z" fill="#d5dde3" stroke="{LINE}" stroke-width="1.4"/>'
    )
    parts.append('<line x1="872" y1="158" x2="872" y2="208" stroke="{0}" stroke-width="4"/>'.format(HEAD))
    parts.append('<circle cx="872" cy="156" r="5" fill="{0}"/>'.format(HEAD))
    parts.append('<text class="sm" x="944" y="168">M8 · 10.9</text>')
    parts.append(
        f'<path d="M848,148 H930 V178 H888 V210 H848 Z" fill="#e7eef6" stroke="{PROX}" stroke-width="1.6"/>'
    )
    parts.append('<text class="sm" x="700" y="230">Ø20</text>')
    parts.append('<text class="dim" x="836" y="236">шип 28×10, галтель R3</text>')
    parts.append('<text class="sm" x="848" y="140">накладка 6 мм</text>')

    # end view
    parts.append('<text class="sm" x="636" y="280">Вид с торца</text>')
    cx, cy = 760, 360
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="46" fill="none" stroke="#c5ced6" stroke-width="1" stroke-dasharray="4 3"/>')
    # flats: rect 46 wide (diameter) by 23 tall (10 mm if dia is 46px => 10mm is 23px)
    parts.append(
        f'<rect x="{cx-46}" y="{cy-16}" width="92" height="32" fill="#d5dde3" stroke="{LINE}" stroke-width="1.6"/>'
    )
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="#fff" stroke="{HEAD}" stroke-width="2"/>')
    # angle wrapping
    parts.append(
        f'<path d="M{cx-58},{cy-40} H{cx+58} V{cy-16} H{cx-30} V{cy+40} H{cx-58} Z" fill="none" stroke="{PROX}" stroke-width="2"/>'
    )
    parts.append(f'<text class="sm" x="{cx+70}" y="{cy-8}">лыски до 10 мм</text>')
    parts.append(f'<text class="sm" x="{cx+70}" y="{cy+10}">болт на срез</text>')
    parts.append(f'<text class="dim" x="{cx-46}" y="{cy+70}">пунктир — исходный Ø20</text>')
    parts.append(
        '<text class="sm" x="636" y="468">Момент передают лыски. Болт держит шип и работает на срез.</text>'
    )
    parts.append(
        '<text class="sm" x="636" y="486">Галтель R3 обязательна: без неё вал треснет у корня.</text>'
    )

    # ===== panel 3: elbow =====
    panel(parts, 28, 556, 570, 450, "3 · Локоть")
    # two chords coming from the left, elbow box, two chords leaving
    def chord(x1, x2, y, color):
        parts.append(
            f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="8" stroke-linecap="round"/>'
        )
    chord(50, 230, 640, PROX)
    chord(50, 230, 860, PROX)
    chord(330, 540, 640, DIST)
    chord(330, 860, 860, DIST) if False else chord(330, 540, 860, DIST)
    # elbow frame
    parts.append(
        f'<rect x="214" y="616" width="120" height="268" rx="3" fill="#fff" stroke="{HEAD}" stroke-width="1.8"/>'
    )
    # pins
    for y in (640, 860):
        parts.append(f'<circle cx="274" cy="{y}" r="11" fill="#fff" stroke="{HEAD}" stroke-width="2.5"/>')
        parts.append(f'<circle cx="274" cy="{y}" r="3" fill="{HEAD}"/>')
    parts.append(
        '<line x1="274" y1="620" x2="274" y2="880" stroke="{0}" stroke-width="1.2" stroke-dasharray="4 3"/>'.format(HEAD)
    )
    parts.append('<text class="lab halo" x="300" y="750">ось пальцев</text>')
    parts.append('<text class="sm halo" x="300" y="768">вертикальна</text>')
    parts.append('<text class="sm" x="60" y="626">плечо 1</text>')
    parts.append('<text class="sm" x="400" y="626">плечо 3</text>')
    parts.append('<text class="dim" x="300" y="900">Ø12, бронзовая втулка, шплинт снизу</text>')
    parts.append(
        '<text class="sm" x="48" y="948">Оба пальца на одной вертикали, иначе ферму скрутит.</text>'
    )
    parts.append(
        '<text class="sm" x="48" y="968">На полном вылете угол между плечами 44° — торцы подрезать.</text>'
    )
    # redraw chords over the box edge so they look continuous into the bushes
    chord(50, 250, 640, PROX)
    chord(298, 540, 640, DIST)
    chord(50, 250, 860, PROX)
    chord(298, 540, 860, DIST)

    # ===== panel 4: head, same orientation as the plan view =====
    panel(parts, 614, 556, 558, 450, "4 · Голова, вид сверху")
    parts.append(
        f'<line x1="660" y1="640" x2="860" y2="690" stroke="{DIST}" stroke-width="8" stroke-linecap="round"/>'
    )
    parts.append(
        f'<line x1="660" y1="900" x2="860" y2="850" stroke="{DIST}" stroke-width="8" stroke-linecap="round"/>'
    )
    parts.append(
        '<rect x="840" y="640" width="280" height="250" rx="6" fill="#f3d2c4" stroke="{0}" stroke-width="1.8"/>'.format(HEAD)
    )
    for y, name in ((690, "плечо 3"), (850, "плечо 4")):
        parts.append(f'<circle cx="860" cy="{y}" r="16" fill="#fff" stroke="{HEAD}" stroke-width="2.4"/>')
        parts.append(f'<circle cx="860" cy="{y}" r="4" fill="{HEAD}"/>')
        parts.append(f'<text class="sm halo" x="830" y="{y-22}" text-anchor="end">{name}</text>')
    parts.append('<rect x="960" y="735" width="54" height="54" rx="4" fill="#fff" stroke="{0}"/>'.format(LINE))
    parts.append('<text class="sm" x="987" y="766" text-anchor="middle">инструмент</text>')
    dim_v(parts, 1090, 690, 850, "180", right=True)
    parts.append('<text class="sm" x="660" y="960">Те же пальцы Ø12. Лист 6–8 мм. С инструментом до 2 кг.</text>')
    parts.append('<text class="sm" x="660" y="980">180 мм — как между валами, иначе голову развернёт.</text>')

    save("04-nodes.svg", parts, w, h)


if __name__ == "__main__":
    fig_kinematics()
    fig_belts()
    fig_side()
    fig_nodes()
