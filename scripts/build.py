#!/usr/bin/env python3
"""Builds the SVG artwork for the profile README.

Run `python3 scripts/build.py` from the repo root. It only needs the Python
standard library and writes everything into assets/.

  hero.svg                 the board. One file, used on both GitHub themes.
  row-<slug>-<theme>.svg   one flat row per project, plus one for the toolkit

Edit the data below (HANDLE, AGE, TAGLINE, PROJECTS, TOOLS) and rebuild.
"""
from pathlib import Path
from xml.sax.saxutils import escape

HANDLE = "3ch0less"
AGE = 18
TAGLINE = ["IoT pentesting", "hardware hacking", "AI", "security"]
DATE_CODE = "2646"  # year 26, week 46: laser-marked on the chips

PROJECTS = [
    dict(
        slug="lumasphere",
        title="lumasphere",
        meta="NASA SPACE APPS CHALLENGE 2026",
        desc="The whole sky in infrared. Explore NASA SPHEREx's all-sky map in 102 colors and watch it change.",
    ),
    dict(
        slug="pvg100e-root",
        title="pvg100e-root",
        meta="ANDROID · QUALCOMM EDL",
        desc="Rooting the Palm Phone through Qualcomm EDL and Magisk: full guide, patched edl tool, backup scripts.",
    ),
    dict(
        slug="roblox-2016-arm64",
        title="roblox-2016-arm64",
        meta="C++ · APPLE SILICON",
        desc="The 2016 Roblox client ported to run natively on Apple Silicon, with shaders and offline play working.",
    ),
]

TOOLS = [
    ("RECON", ["Ghidra", "radare2", "Wireshark", "nmap", "tcpdump", "Burp Suite"]),
    ("BUILD", ["Python", "C / C++", "JS / TS", "Linux", "Docker", "Android"]),
]

# The board itself: solder mask over bare laminate, mask over copper, and so on.
# Swap base/pour/ant/edge for another mask colour, e.g. matte black:
#   base="#0a0c0f", pour="#171c22", ant="#2a323d", edge="#3a424d"
BOARD = dict(
    base="#0a2c21", pour="#0f4133", ant="#1a6a52", edge="#1d5c48",
    silk="#eef4ef", cu0="#f3c876", cu1="#c88a2a", led="#7cc8ff",
)

# Page colours for the flat rows under the board, one set per GitHub theme.
PAGE = {
    "dark": dict(ink="#e6edf3", dim="#8b949e", rule="#262c36", gold="#dba545", hole="#0d1117"),
    "light": dict(ink="#1f2328", dim="#59636e", rule="#d8dee4", gold="#a8771a", hole="#ffffff"),
}

MONO = 'ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono","DejaVu Sans Mono",monospace'
SANS = '-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif'
W = 1200


def n(v):
    """Compact number formatting."""
    return f"{v:.2f}".rstrip("0").rstrip(".")


# --------------------------------------------------------------- lettering
# Monoline glyphs on a 4x6 grid, drawn like routed traces: 45 degree bends,
# and a via wherever a stroke ends in open space. (width, strokes, vias)
GLYPHS = {
    "3": (4, [[(0, 0), (3, 0), (4, 1), (4, 2), (3, 3), (1, 3)],
              [(3, 3), (4, 4), (4, 5), (3, 6), (0, 6)]], [(0, 0), (1, 3), (0, 6)]),
    "c": (4, [[(4, 2), (1, 2), (0, 3), (0, 5), (1, 6), (4, 6)]], [(4, 2), (4, 6)]),
    "h": (4, [[(0, 0), (0, 6)], [(0, 3), (1, 2), (3, 2), (4, 3), (4, 6)]],
          [(0, 0), (0, 6), (4, 6)]),
    "0": (4, [[(1, 0), (3, 0), (4, 1), (4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0)],
              [(1.3, 4.05), (2.7, 1.95)]], []),
    "l": (2, [[(0, 0), (0, 5), (1, 6), (2, 6)]], [(0, 0), (2, 6)]),
    "e": (4, [[(0, 4), (4, 4), (4, 3), (3, 2), (1, 2), (0, 3), (0, 5), (1, 6), (4, 6)]],
          [(4, 6)]),
    "s": (4, [[(4, 2), (1, 2), (0, 3), (1, 4), (3, 4), (4, 5), (3, 6), (0, 6)]],
          [(4, 2), (0, 6)]),
    "a": (4, [[(0, 2), (3, 2), (4, 3), (4, 6)], [(4, 4), (1, 4), (0, 5), (1, 6), (4, 6)]], [(0, 2)]),
    "b": (4, [[(0, 0), (0, 6), (3, 6), (4, 5), (4, 3), (3, 2), (1, 2), (0, 3)]], [(0, 0)]),
    "d": (4, [[(4, 0), (4, 6), (1, 6), (0, 5), (0, 3), (1, 2), (3, 2), (4, 3)]], [(4, 0)]),
    "g": (4, [[(4, 6), (1, 6), (0, 5), (0, 3), (1, 2), (4, 2), (4, 7), (3, 8), (0, 8)]], [(0, 8)]),
    "i": (0, [[(0, 2), (0, 6)]], [(0, 0.5)]),
    "k": (4, [[(0, 0), (0, 6)], [(4, 2), (2, 4), (4, 6)], [(0, 4), (2, 4)]], [(0, 0), (4, 2), (4, 6)]),
    "m": (6, [[(0, 2), (0, 6)], [(0, 3), (1, 2), (2, 2), (3, 3), (3, 6)],
              [(3, 3), (4, 2), (5, 2), (6, 3), (6, 6)]], [(0, 2)]),
    "n": (4, [[(0, 2), (0, 6)], [(0, 3), (1, 2), (3, 2), (4, 3), (4, 6)]], [(0, 2)]),
    "o": (4, [[(1, 2), (3, 2), (4, 3), (4, 5), (3, 6), (1, 6), (0, 5), (0, 3), (1, 2)]], []),
    "p": (4, [[(0, 2), (0, 8)], [(0, 3), (1, 2), (3, 2), (4, 3), (4, 5), (3, 6), (0, 6)]], [(0, 8)]),
    "r": (3, [[(0, 2), (0, 6)], [(0, 3), (1, 2), (3, 2)]], [(3, 2)]),
    "t": (3, [[(1, 0), (1, 5), (2, 6), (3, 6)], [(0, 2), (3, 2)]], [(1, 0), (3, 6)]),
    "u": (4, [[(0, 2), (0, 5), (1, 6), (3, 6), (4, 5)], [(4, 2), (4, 6)]], [(0, 2), (4, 2)]),
    "v": (4, [[(0, 2), (0, 4), (2, 6), (4, 4), (4, 2)]], [(0, 2), (4, 2)]),
    "w": (6, [[(0, 2), (0, 5), (1, 6), (2, 6), (3, 5), (3, 3)], [(3, 5), (4, 6), (5, 6), (6, 5), (6, 2)]],
          [(0, 2), (6, 2)]),
    "x": (4, [[(0, 2), (4, 6)], [(4, 2), (0, 6)]], [(0, 2), (4, 2)]),
    "1": (2, [[(0, 1), (1, 0), (1, 6)], [(0, 6), (2, 6)]], [(0, 1)]),
    "2": (4, [[(0, 1), (1, 0), (3, 0), (4, 1), (4, 2), (0, 6), (4, 6)]], [(0, 1), (4, 6)]),
    "4": (4, [[(3, 6), (3, 0), (0, 3), (0, 4), (4, 4)]], [(4, 4)]),
    "6": (4, [[(3, 0), (1, 0), (0, 1), (0, 5), (1, 6), (3, 6), (4, 5), (4, 4), (3, 3), (0, 3)]], [(3, 0)]),
    "-": (3, [[(0, 4), (3, 4)]], [(0, 4), (3, 4)]),
}


def glyph_geometry(text, x, y, u, gap=1.6):
    """Returns (path strings, via points, width). x,y is the top-left of the cap height."""
    paths, vias, cx = [], [], x
    for ch in text:
        gw, strokes, vs = GLYPHS[ch]
        for s in strokes:
            p = [(cx + px * u, y + py * u) for px, py in s]
            closed = s[0] == s[-1]
            paths.append("M" + " L".join(f"{n(a)},{n(b)}" for a, b in (p[:-1] if closed else p)) + ("Z" if closed else ""))
        vias += [(cx + vx * u, y + vy * u) for vx, vy in vs]
        cx += (gw + gap) * u
    return paths, vias, cx - gap * u - x


# ------------------------------------------------------------------- hero
def hero(b):
    """A small IoT board, top view: USB in, regulator, MCU, SPI flash, an
    unpopulated UART header, and a meandered antenna in its keep-out."""
    H = 548
    X0, Y0, X1, Y1 = 24, 14, 1188, 534
    base = b["base"]
    moat_s, moat_f, cu, gold, silk, parts, drills = [], [], [], [], [], [], []

    # ---- primitives -----------------------------------------------------
    def trace(d, w=3):
        moat_s.append(f'<path d="{d}" stroke-width="{n(w + 8)}"/>')
        cu.append(f'<path d="{d}" stroke-width="{n(w)}"/>')

    def rpad(x, y, r, hole=0):
        moat_f.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r + 4)}"/>')
        gold.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}"/>')
        if hole:
            gold.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(hole)}" fill="{base}"/>')

    def spad(x, y, w, h, grow=3.2):
        moat_f.append(f'<rect x="{n(x - w / 2 - grow)}" y="{n(y - h / 2 - grow)}" width="{n(w + 2 * grow)}" height="{n(h + 2 * grow)}"/>')
        gold.append(f'<rect x="{n(x - w / 2)}" y="{n(y - h / 2)}" width="{n(w)}" height="{n(h)}"/>')

    def via(x, y):
        moat_f.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="6.6"/>')
        gold.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="3.7"/><circle cx="{n(x)}" cy="{n(y)}" r="1.5" fill="{base}"/>')

    def label(x, y, s, size=9.5, anchor="start", weight=600, ls=0.8, op=0.9):
        silk.append(
            f'<text x="{n(x)}" y="{n(y)}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" '
            f'letter-spacing="{ls}" fill-opacity="{op}">{escape(s)}</text>'
        )

    def passive(x, y, kind="c", vertical=False):
        """An 0402-ish two-terminal part. x,y is its centre."""
        body = {"c": "#b6976b", "r": "#191b1f", "l": "#3b4350"}[kind]
        if vertical:
            spad(x, y - 5.4, 9, 5.2), spad(x, y + 5.4, 9, 5.2)
            parts.append(
                f'<rect x="{n(x - 3.6)}" y="{n(y - 7.2)}" width="7.2" height="14.4" fill="url(#tin)"/>'
                f'<rect x="{n(x - 3.6)}" y="{n(y - 4)}" width="7.2" height="8" fill="{body}"/>'
            )
        else:
            spad(x - 5.4, y, 5.2, 9), spad(x + 5.4, y, 5.2, 9)
            parts.append(
                f'<rect x="{n(x - 7.2)}" y="{n(y - 3.6)}" width="14.4" height="7.2" fill="url(#tin)"/>'
                f'<rect x="{n(x - 4)}" y="{n(y - 3.6)}" width="8" height="7.2" fill="{body}"/>'
            )

    def package(x, y, w, h, lines, dot=True):
        """Black moulded body with laser marking. x,y is its top-left."""
        out = [
            f'<rect x="{n(x + 2)}" y="{n(y + 3)}" width="{w}" height="{h}" rx="2" fill="#000" fill-opacity=".35"/>',
            f'<rect x="{n(x)}" y="{n(y)}" width="{w}" height="{h}" rx="2" fill="#17191d" stroke="#2a2e35"/>',
            f'<rect x="{n(x)}" y="{n(y)}" width="{w}" height="{h}" rx="2" fill="url(#sheen)"/>',
        ]
        if dot:
            out.append(f'<circle cx="{n(x + 9)}" cy="{n(y + 9)}" r="3" fill="#0b0c0e" stroke="#30353d" stroke-width=".8"/>')
        ty = y + h / 2 - (len(lines) - 1) * 7 + 4
        for i, (s, size, weight) in enumerate(lines):
            out.append(
                f'<text class="mono" x="{n(x + w / 2)}" y="{n(ty + i * 15)}" text-anchor="middle" font-size="{size}" '
                f'font-weight="{weight}" letter-spacing=".6" fill="#98a1ac">{escape(s)}</text>'
            )
        parts.append("".join(out))

    # ---- USB-C, on the left edge ------------------------------------------
    ucy = 412
    for k in range(8):
        spad(86, 388 + 7 * k, 11, 3.6, grow=2.6)
    for yy in (367.5, 456.5):
        for xx in (36, 64):
            spad(xx, yy, 15, 10)
    parts.append(
        f'<rect x="12" y="{ucy - 37}" width="68" height="80" rx="3" fill="#000" fill-opacity=".3"/>'
        f'<rect x="10" y="{ucy - 40}" width="68" height="80" rx="3" fill="url(#shell)" stroke="#6f7781" stroke-width="1"/>'
        f'<path d="M22,{ucy - 40} V{ucy + 40} M66,{ucy - 40} V{ucy + 40}" stroke="#5e666f" stroke-opacity=".55" fill="none"/>'
        f'<rect x="30" y="{ucy - 22}" width="20" height="7" fill="#5a626c" fill-opacity=".7"/>'
        f'<rect x="30" y="{ucy + 15}" width="20" height="7" fill="#5a626c" fill-opacity=".7"/>'
    )
    label(84, 374, "J2")

    # ---- USB pair, with one jog, running to the MCU --------------------------
    trace("M91,409 H200 L224,385 H600 L624,409 H806 L811.5,414.5 H823")
    trace("M91,416 H202.9 L226.9,392 H597.1 L621.1,416 H803 L812.5,425.5 H823")

    # ---- regulator: VBUS in, 3V3 rail out ----------------------------------
    trace("M91,437 H137 L159.5,459.5 V467", 4.5)
    trace("M176.5,467 V455.5 L184.5,447.5 H823", 5)
    trace("M168,489 V500")
    via(168, 504)
    for xx, yy in ((159.5, 468.5), (176.5, 468.5), (159.5, 487.5), (168, 487.5), (176.5, 487.5)):
        spad(xx, yy, 5, 6.5, grow=2.4)
    parts.append(
        "".join(f'<rect x="{n(xx - 2)}" y="{yy}" width="4" height="6" fill="url(#tin)"/>' for xx, yy in
                ((159.5, 466), (176.5, 466), (159.5, 484), (168, 484), (176.5, 484)))
    )
    package(153, 471, 30, 14, [], dot=False)
    label(190, 482, "U3")
    passive(112, 448, "c", vertical=True)
    trace("M112,442.6 V437")
    via(112, 464)
    passive(214, 458.5, "c", vertical=True)
    trace("M214,453 V447.5")
    via(214, 475)
    label(122, 458, "C1"), label(224, 468, "C2")

    # ---- crystal and its load caps -------------------------------------------
    trace("M732,350 H791.5 L823,381.5")
    trace("M700,350 V376 L716.5,392.5 H823")
    spad(700, 350, 10, 14), spad(732, 350, 10, 14)
    parts.append(
        '<rect x="696" y="343" width="44" height="18" rx="2" fill="#000" fill-opacity=".3"/>'
        '<rect x="694" y="341" width="44" height="18" rx="2" fill="url(#shell)" stroke="#6f7781" stroke-width="1"/>'
        '<text class="mono" x="716" y="353.4" text-anchor="middle" font-size="8.5" font-weight="600" fill="#4a525c">16.000</text>'
    )
    for xx in (700, 732):
        trace(f"M{xx},341 V330")
        passive(xx, 324.6, "c", vertical=True)
        via(xx, 308)
    label(746, 346, "Y1")

    # ---- MCU ------------------------------------------------------------------
    mx, my, half, ll = 884, 420, 52, 9
    offs = [(k - 3.5) * 11 for k in range(8)]
    for o in offs:
        for px, py, pw, ph in (
            (mx - half - ll / 2 - 1, my + o, ll + 2, 5.2), (mx + half + ll / 2 + 1, my + o, ll + 2, 5.2),
            (mx + o, my - half - ll / 2 - 1, 5.2, ll + 2), (mx + o, my + half + ll / 2 + 1, 5.2, ll + 2),
        ):
            spad(px, py, pw, ph, grow=3)
        parts.append(
            f'<rect x="{n(mx - half - ll)}" y="{n(my + o - 1.9)}" width="{ll}" height="3.8" fill="url(#tin)"/>'
            f'<rect x="{n(mx + half)}" y="{n(my + o - 1.9)}" width="{ll}" height="3.8" fill="url(#tin)"/>'
            f'<rect x="{n(mx + o - 1.9)}" y="{n(my - half - ll)}" width="3.8" height="{ll}" fill="url(#tin)"/>'
            f'<rect x="{n(mx + o - 1.9)}" y="{n(my + half)}" width="3.8" height="{ll}" fill="url(#tin)"/>'
        )
    package(mx - half, my - half, 2 * half, 2 * half, [(f"3CH0-{AGE}", 15, 700), (f"UAE {DATE_CODE}", 9.5, 500)])
    label(mx - half - 4, my - half - 14, "U1", anchor="end")

    # decoupling, top and bottom
    trace("M845.5,359 V346"), trace("M856.5,359 V346")
    passive(851, 341, "c")
    trace("M900.5,481 V494"), trace("M911.5,481 V494")
    passive(906, 499, "c")

    # debug pads
    trace("M856.5,481 V499"), trace("M878.5,481 V499")
    rpad(856.5, 506, 6.5), rpad(878.5, 506, 6.5)
    label(844, 510, "SWD", anchor="end")

    # ---- RF: matching network, then out to the antenna -------------------------
    trace("M889.5,359 V266 L925.5,230 H998 L1024,204 V196", 4)
    passive(962, 230, "l")
    for xx in (940, 984):
        passive(xx, 239.4, "c", vertical=True)
        via(xx, 256)
    label(962, 220, "L1", anchor="middle")

    # ---- SPI flash ---------------------------------------------------------------
    fx, fy = 988, 412
    lead_y = [420.5, 433.5, 446.5, 459.5]
    for src, dst, bend in zip((414.5, 425.5, 436.5, 447.5), lead_y, (960, 958, 956, 954)):
        trace(f"M945,{src} H{bend} L{n(bend + dst - src)},{dst} H978")
    for ly in lead_y:
        spad(fx - 6, ly, 13, 6), spad(fx + 50, ly, 13, 6)
        parts.append(
            f'<rect x="{fx - 11}" y="{ly - 2.2}" width="11" height="4.4" fill="url(#tin)"/>'
            f'<rect x="{fx + 44}" y="{ly - 2.2}" width="11" height="4.4" fill="url(#tin)"/>'
        )
    package(fx, fy, 44, 56, [("25Q64", 10, 700), (DATE_CODE, 8.5, 500)])
    label(fx + 22, fy - 8, "U2", anchor="middle")
    trace("M1042,420.5 H1052"), via(1056, 420.5)

    # ---- J1: the UART header, left unpopulated -------------------------------------
    jx = 1120
    for (jy, name), k in zip(((366, "GND"), (396, "TX"), (426, "RX"), (456, "3V3")), range(4)):
        if k == 0:
            cu.append(f'<path d="M{jx - 18},{jy} H{jx + 18} M{jx},{jy - 18} V{jy + 18}" stroke-width="4"/>')
            moat_f.append(f'<rect x="{jx - 14}" y="{jy - 14}" width="28" height="28"/>')
            gold.append(f'<rect x="{jx - 10}" y="{jy - 10}" width="20" height="20"/><circle cx="{jx}" cy="{jy}" r="4.2" fill="{base}"/>')
        else:
            rpad(jx, jy, 10, 4.2)
        label(jx + 22, jy + 4.6, name, size=13, weight=700, ls=0.4, op=1)
    silk.append(f'<rect x="{jx - 16}" y="350" width="32" height="122" fill="none" stroke="{b["silk"]}" stroke-width="1.6"/>')
    label(jx - 16, 342, "J1 UART", size=10)
    trace("M945,381.5 H1080.5 L1095,396 H1110")
    trace("M945,392.5 H1062.5 L1096,426 H1110")
    trace(f"M{jx},466 V488"), via(jx, 492)

    # ---- status LED ------------------------------------------------------------------
    trace("M945,458.5 H951.5 L985,492 H1082")
    via(1086, 492)
    passive(1013, 492, "r")
    spad(1046.6, 492, 5.2, 9), spad(1057.4, 492, 5.2, 9)
    parts.append(
        '<rect x="1044.8" y="488.4" width="14.4" height="7.2" fill="url(#tin)"/>'
        '<rect x="1048" y="488.4" width="8" height="7.2" fill="#eaf6ff"/>'
        '<circle class="led" cx="1052" cy="492" r="15" fill="url(#glow)"/>'
    )
    label(1013, 482, "R1", anchor="middle"), label(1052, 482, "D1", anchor="middle")

    # ---- antenna keep-out, stitched with ground vias ----------------------------------
    kx, ky = 1004, 196
    for yy in range(38, 190, 25):
        via(kx - 10, yy)
    for xx in range(1046, 1176, 25):
        via(xx, ky + 10)
    ant = "M1024,196 V60 H1052 V132 H1080 V60 H1108 V132 H1136 V60 H1164 V164 M1024,96 H1004"
    label(1172, 186, "ANT1", anchor="end")

    # ---- fiducials, mounting holes -------------------------------------------------------
    for fx_, fy_ in ((268, 500), (952, 52)):
        moat_f.append(f'<circle cx="{fx_}" cy="{fy_}" r="10"/>')
        gold.append(f'<circle cx="{fx_}" cy="{fy_}" r="4"/>')
    for hx, hy in ((58, 50), (58, 498), (1158, 504)):
        moat_f.append(f'<circle cx="{hx}" cy="{hy}" r="18"/>')
        gold.append(f'<circle cx="{hx}" cy="{hy}" r="13.5"/>')
        drills.append(f'<circle cx="{hx}" cy="{hy}" r="8"/>')

    # ---- the handle, as exposed copper -----------------------------------------------------
    u, nx, ny = 19, 96, 104
    paths, vias_, _ = glyph_geometry(HANDLE, nx, ny, u)
    sw = u * 0.46
    name_moat = "".join(f'<path d="{d}"/>' for d in paths)
    name = "".join(
        f'<path class="name" pathLength="1" d="{d}" style="animation-delay:{n(0.15 + i * 0.07)}s"/>' for i, d in enumerate(paths)
    )
    name_vias = "".join(
        f'<g class="nvia" style="animation-delay:{n(0.9 + i * 0.05)}s"><circle cx="{n(x)}" cy="{n(y)}" r="{n(u * 0.43)}" fill="url(#gold)"/>'
        f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(u * 0.17)}" fill="{base}"/></g>'
        for i, (x, y) in enumerate(vias_)
    )
    sep = f'<tspan fill="{b["cu0"]}" dx="10"> · </tspan>'
    tag = sep.join(f"<tspan{' dx=\"10\"' if k else ''}>{escape(s)}</tspan>" for k, s in enumerate(TAGLINE))
    title = f"{HANDLE}: {', '.join(TAGLINE)}. Based in the UAE."

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(title)}">
  <title>{escape(title)}</title>
  <defs>
    <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{b['cu0']}"/><stop offset="1" stop-color="{b['cu1']}"/></linearGradient>
    <linearGradient id="goldn" gradientUnits="userSpaceOnUse" x1="0" y1="{ny}" x2="0" y2="{ny + 6 * u}"><stop offset="0" stop-color="{b['cu0']}"/><stop offset="1" stop-color="{b['cu1']}"/></linearGradient>
    <linearGradient id="tin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e3e7ec"/><stop offset="1" stop-color="#a9b1bb"/></linearGradient>
    <linearGradient id="shell" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d9dee4"/><stop offset=".5" stop-color="#aab2bc"/><stop offset="1" stop-color="#c6ccd3"/></linearGradient>
    <linearGradient id="sheen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".09"/><stop offset=".55" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <linearGradient id="light" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".045"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <radialGradient id="glow"><stop offset="0" stop-color="{b['led']}" stop-opacity=".95"/><stop offset=".35" stop-color="{b['led']}" stop-opacity=".4"/><stop offset="1" stop-color="{b['led']}" stop-opacity="0"/></radialGradient>
    <mask id="drill"><rect width="{W}" height="{H}" fill="#fff"/><g fill="#000">{''.join(drills)}</g></mask>
  </defs>
  <style>
    .mono{{font-family:{MONO}}}
    .name{{fill:none;stroke:url(#goldn);stroke-width:{n(sw)};stroke-linecap:round;stroke-linejoin:miter;stroke-dasharray:1;animation:draw 1.2s cubic-bezier(.65,0,.2,1) both}}
    .nvia{{animation:pop .45s ease-out both}}
    @keyframes draw{{0%{{stroke-dashoffset:1;opacity:0}}6%{{opacity:1}}100%{{stroke-dashoffset:0;opacity:1}}}}
    @keyframes pop{{0%{{opacity:0}}100%{{opacity:1}}}}
    .led{{animation:led 2.4s ease-in-out infinite}}
    @keyframes led{{0%,100%{{opacity:1}}50%{{opacity:.12}}}}
    @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
  </style>
  <g mask="url(#drill)">
    <!-- laminate and solder mask -->
    <rect x="{X0}" y="{Y0}" width="{X1 - X0}" height="{Y1 - Y0}" rx="5" fill="{base}"/>
    <!-- copper pour, pulled back from the edge and out of the antenna keep-out -->
    <path d="M{X0 + 9},{Y0 + 9} H{kx} V{ky} H{X1 - 9} V{Y1 - 9} H{X0 + 9} Z" fill="{b['pour']}"/>
    <!-- clearance around everything that is not ground -->
    <g fill="none" stroke="{base}" stroke-linecap="round" stroke-linejoin="round">{''.join(moat_s)}</g>
    <g fill="none" stroke="{base}" stroke-width="{n(sw + 13)}" stroke-linecap="round" stroke-linejoin="round">{name_moat}</g>
    <g fill="{base}">{''.join(moat_f)}</g>
    <!-- tracks, under mask -->
    <g fill="none" stroke="{b['pour']}" stroke-linecap="round" stroke-linejoin="miter">{''.join(cu)}</g>
    <path d="{ant}" fill="none" stroke="{b['ant']}" stroke-width="7" stroke-linejoin="miter"/>
    <!-- exposed copper -->
    <g fill="url(#gold)">{''.join(gold)}</g>
    <g>{name}{name_vias}</g>
    <!-- silkscreen -->
    <g class="mono" fill="{b['silk']}">
      <text x="{nx}" y="66" font-size="15" letter-spacing="3" font-weight="600" fill-opacity=".72">REV {AGE} · BASED IN THE UAE</text>
      <text x="{nx}" y="272" font-size="23" font-weight="500">{tag}</text>
      {''.join(silk)}
    </g>
    <!-- parts -->
    {''.join(parts)}
    <!-- a little light across the mask, and the board edge -->
    <rect x="{X0}" y="{Y0}" width="{X1 - X0}" height="{Y1 - Y0}" rx="5" fill="url(#light)"/>
    <rect x="{X0 + .75}" y="{Y0 + .75}" width="{X1 - X0 - 1.5}" height="{Y1 - Y0 - 1.5}" rx="4.5" fill="none" stroke="{b['edge']}" stroke-width="1.5"/>
  </g>
</svg>
"""


# ------------------------------------------------------- rows under the board
def row(title, meta, desc, t, link=True, rule=True):
    """Square pad, a name, where it came from, one line about it."""
    H = 92
    arrow = f'<path d="M{W - 16},36 l11,-11 m-8.5,0 h8.5 v8.5" fill="none" stroke="{t["gold"]}" stroke-width="2.2" stroke-linecap="square"/>'
    body = f"""  <rect x="1" y="17" width="18" height="18" fill="{t['gold']}"/><circle cx="10" cy="26" r="3.6" fill="{t['hole']}"/>
  <text class="mono" x="40" y="35" font-size="26" font-weight="700" fill="{t['ink']}">{escape(title)}</text>
  <text class="mono" x="{W - (30 if link else 2)}" y="33" text-anchor="end" font-size="13" letter-spacing="2.4" font-weight="600" fill="{t['dim']}">{escape(meta)}</text>
  {arrow if link else ''}
  <text class="sans" x="40" y="68" font-size="19.5" fill="{t['dim']}">{escape(desc)}</text>
  {f'<path d="M0,{H - .5} H{W}" stroke="{t["rule"]}"/>' if rule else ''}
"""
    return flat(H, body, f"{title}: {desc}")


def flat(h, body, title):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-label="{escape(title)}">
  <title>{escape(title)}</title>
  <style>.mono{{font-family:{MONO}}}.sans{{font-family:{SANS}}}</style>
{body}</svg>
"""


def main():
    out = Path(__file__).resolve().parent.parent / "assets"
    out.mkdir(exist_ok=True)
    files = {"hero.svg": hero(BOARD)}
    tools = " · ".join(item for _, items in TOOLS for item in items)
    for name, t in PAGE.items():
        files[f"row-toolkit-{name}.svg"] = row("toolkit", " + ".join(g for g, _ in TOOLS), tools, t, link=False, rule=False)
        for p in PROJECTS:
            files[f"row-{p['slug']}-{name}.svg"] = row(p["title"], p["meta"], p["desc"], t)
    for stale in out.glob("*.svg"):
        if stale.name not in files:
            stale.unlink()
    for fname, content in files.items():
        (out / fname).write_text(content)
    print(f"wrote {len(files)} files to {out}")


if __name__ == "__main__":
    main()
