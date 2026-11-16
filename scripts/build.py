#!/usr/bin/env python3
"""Builds the SVG artwork for the profile README.

Run `python3 scripts/build.py` from the repo root. Every asset is written
twice (dark and light) into assets/ and picked by GitHub with <picture>.

Edit the data at the top (AGE, HANDLE, PROJECTS, PINS) and rebuild.
Nothing here needs anything beyond the Python standard library.
"""
import math
import random
from pathlib import Path
from xml.sax.saxutils import escape

HANDLE = "3ch0less"
AGE = 18
TAGLINE = ["IoT pentesting", "hardware hacking", "AI", "security"]

DATE_CODE = "2646"  # year 26, week 46: stamped on the toolkit chip

# Titles are drawn with the trace lettering, so they can only use glyphs
# that exist in GLYPHS below (lowercase, a few digits, hyphen).
PROJECTS = [
    dict(
        slug="lumasphere",
        viz="sky",
        meta="NASA SPACE APPS CHALLENGE 2026 · UNIVERSITY OF DUBAI",
        title="lumasphere",
        desc=[
            "The whole sky in infrared. Step inside NASA SPHEREx's",
            "all-sky map, tune through 102 infrared colors, and watch",
            "any patch of sky change from one visit to the next.",
        ],
        stack=["Python", "FastAPI", "astropy", "JavaScript", "Docker"],
    ),
    dict(
        slug="pvg100e-root",
        viz="boot",
        meta="ANDROID · QUALCOMM EDL · REVERSE ENGINEERING",
        title="pvg100e-root",
        desc=[
            "Rooting the Palm Phone through Qualcomm EDL and Magisk,",
            "locked bootloader and all. A full guide, a patched edl",
            "tool, and scripts to back up and restore every partition.",
        ],
        stack=["Python", "EDL / Firehose", "Magisk", "MSM8937"],
    ),
    dict(
        slug="roblox-2016-arm64",
        viz="ret",
        meta="C++ · PORTING · APPLE SILICON",
        title="roblox-2016-arm64",
        desc=[
            "The 2016 Roblox client, ported to run natively on Apple",
            "Silicon. Hundreds of translation units rebuilt for ARM64,",
            "with GLSL shaders and offline play working.",
        ],
        stack=["C++", "ARM64", "macOS", "GLSL"],
    ),
]

PINS_LEFT = ["Ghidra", "radare2", "Wireshark", "nmap", "tcpdump", "Burp Suite"]
PINS_RIGHT = ["Python", "C / C++", "JS / TS", "Linux", "Docker", "Android"]

THEMES = {
    "dark": dict(
        board0="#0d1016", board1="#07090c", edge="#262d37", grid="#1b212b",
        panel="#05070a", panel_edge="#1f2630",
        cu0="#f3c876", cu1="#c88a2a", cu="#dba545", cu_dim="#dba545", cu_dim_op="0.30",
        silk="#eef1f5", dim="#8a94a3", sig="#4fe3c1", hole="#0d1117",
        chip="#141920", chip_edge="#2c3440", chip_text="#eef1f5", chip_dim="#7d8796",
        page_ink="#e6edf3", page_dim="#7d8590",
        desc="#b9c2cf", lead="#aeb6c2", chip0="#1c222b",
    ),
    "light": dict(
        board0="#fdfcf9", board1="#f3f1ea", edge="#d6d1c4", grid="#e3dfd3",
        panel="#ffffff", panel_edge="#ddd8cb",
        cu0="#c4912f", cu1="#99690f", cu="#a8771a", cu_dim="#a8771a", cu_dim_op="0.38",
        silk="#14181d", dim="#5b6470", sig="#0a8a72", hole="#ffffff",
        chip="#1a1f26", chip_edge="#1a1f26", chip_text="#f2f4f7", chip_dim="#98a1ae",
        page_ink="#1f2328", page_dim="#656d76",
        desc="#3a424d", lead="#8f97a3", chip0="#262c35",
    ),
}

MONO = 'ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono","DejaVu Sans Mono",monospace'
SANS = '-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif'

W = 1200


def n(v):
    """Compact number formatting."""
    return f"{v:.2f}".rstrip("0").rstrip(".")


def pts(points):
    return " ".join(f"{n(x)},{n(y)}" for x, y in points)


def base_css(t):
    return f"""
    .mono{{font-family:{MONO}}}
    .sans{{font-family:{SANS}}}
    .silk{{fill:{t['silk']}}}
    .dim{{fill:{t['dim']}}}
    .cu{{fill:{t['cu']}}}
    .sig{{fill:{t['sig']}}}
    .trace{{fill:none;stroke:{t['cu']};stroke-linecap:round;stroke-linejoin:round}}
    .bg{{fill:none;stroke:{t['cu_dim']};stroke-opacity:{t['cu_dim_op']};stroke-width:3;stroke-linecap:round;stroke-linejoin:round}}
    @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}"""


def svg(w, h, t, body, css="", defs="", title=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(title)}">
  <title>{escape(title)}</title>
  <defs>
    <linearGradient id="board" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{t['board0']}"/><stop offset="1" stop-color="{t['board1']}"/>
    </linearGradient>
    <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{t['cu0']}"/><stop offset="1" stop-color="{t['cu1']}"/>
    </linearGradient>
    <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="12" cy="12" r="1.15" fill="{t['grid']}"/>
    </pattern>{defs}
  </defs>
  <style>{base_css(t)}{css}
  </style>
{body}
</svg>
"""


def board(w, h, t, rx=22):
    return (
        f'  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{rx}" fill="url(#board)" stroke="{t["edge"]}" stroke-width="2"/>\n'
        f'  <rect x="6" y="6" width="{w - 12}" height="{h - 12}" rx="{rx - 5}" fill="url(#dots)"/>\n'
    )


def via(x, y, t, r=8, hole=3.2, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (
        f'<g{c}><circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="url(#gold)"/>'
        f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(hole)}" fill="{t["board1"]}"/></g>'
    )


def mount_hole(x, y, t):
    return (
        f'<circle cx="{x}" cy="{y}" r="11" fill="{t["hole"]}" stroke="{t["cu"]}" stroke-width="3.5"/>'
    )


# --------------------------------------------------------------- lettering
# Monoline glyphs on a 4x6 grid, drawn like routed traces: 45 degree bends,
# and a via wherever a stroke ends in open space.
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
    # the rest of the typeface, used for project titles
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


def lettering(text, x, y, u, t, gap=1.6, animate=True, cls="name", via_cls="nvia", via_r=0.43, hole_r=0.17):
    """Returns (svg, width). x,y is the top-left of the cap height."""
    out, cx, i = [], x, 0
    plen = ' pathLength="1"' if animate else ""
    for ch in text:
        gw, strokes, vias = GLYPHS[ch]
        for s in strokes:
            p = [(cx + px * u, y + py * u) for px, py in s]
            closed = s[0] == s[-1]
            d = "M" + " L".join(f"{n(a)},{n(b)}" for a, b in (p[:-1] if closed else p)) + ("Z" if closed else "")
            style = f' style="animation-delay:{n(0.15 + i * 0.07)}s"' if animate else ""
            out.append(f'<path class="trace {cls}"{plen} d="{d}"{style}/>')
            i += 1
        for vx, vy in vias:
            style = f' style="animation-delay:{n(0.75 + i * 0.07)}s"' if animate else ""
            out.append(
                f'<g class="{via_cls}"{style}><circle cx="{n(cx + vx * u)}" cy="{n(y + vy * u)}" r="{n(u * via_r)}" fill="url(#gold)"/>'
                f'<circle cx="{n(cx + vx * u)}" cy="{n(y + vy * u)}" r="{n(u * hole_r)}" fill="{t["board1"]}"/></g>'
            )
        cx += (gw + gap) * u
    return "\n    ".join(out), cx - gap * u - x


# ------------------------------------------------------------------- hero
def uart_bits(text):
    """8N1 framing: start bit low, 8 data bits LSB first, stop bit high."""
    bits = [1, 1]  # idle
    for b in text.encode("ascii"):
        bits += [0] + [(b >> k) & 1 for k in range(8)] + [1]
    return bits + [1, 1]


def hero(t):
    H = 440
    u = 19
    name_svg, name_w = lettering(HANDLE, 64, 80, u, t)

    # --- logic analyzer capture
    px0, px1, py0, py1 = 64, 1136, 274, 404
    x0, x1 = px0 + 22, px1 - 22
    hi, lo = 322, 350
    bits = uart_bits(HANDLE)
    bw = (x1 - x0) / len(bits)
    d, length, level = f"M{n(x0)},{hi}", 0.0, 1
    marks = []  # path length at the end of every byte frame
    for k, b in enumerate(bits):
        xa = x0 + k * bw
        if b != level:
            d += f" V{hi if b else lo}"
            length += lo - hi
            level = b
        d += f" H{n(xa + bw)}"
        length += bw
        if k >= 2 and (k - 2) % 10 == 9:
            marks.append(length)
    total = length

    draw_end, hold_end, fade_end = 30.0, 90.0, 95.0  # percent of the loop
    kf, boxes, guides = [], [], []
    for i, ch in enumerate(HANDLE):
        bx = x0 + (2 + 10 * i) * bw
        p = draw_end * marks[i] / total
        kf.append(
            f"@keyframes b{i}{{0%,{n(p)}%{{opacity:0}}{n(p + 1.2)}%,{hold_end}%{{opacity:1}}{fade_end}%,100%{{opacity:0}}}}"
            f".b{i}{{animation:b{i} 16s linear infinite}}"
        )
        mid = bx + 5 * bw
        boxes.append(
            f'<g class="b{i}"><rect x="{n(bx + 3)}" y="364" width="{n(10 * bw - 6)}" height="28" rx="6" fill="{t["sig"]}" fill-opacity="0.10" stroke="{t["sig"]}" stroke-opacity="0.45"/>'
            f'<text class="mono" x="{n(mid)}" y="383.5" text-anchor="middle" font-size="15">'
            f'<tspan class="dim">0x{ord(ch):02X}</tspan><tspan class="silk" font-weight="700" dx="10">{escape(ch)}</tspan></text></g>'
        )
        guides.append(f'<path d="M{n(bx)},314 V358"/>')
    guides.append(f'<path d="M{n(x0 + (2 + 10 * len(HANDLE)) * bw)},314 V358"/>')

    # --- J1 UART header
    pads = [(968, "GND"), (1012, "TX"), (1056, "RX"), (1100, "3V3")]
    py = 128
    j1 = [f'<rect x="946" y="106" width="176" height="44" rx="7" fill="none" stroke="{t["silk"]}" stroke-width="2"/>']
    for k, (pxx, label) in enumerate(pads):
        if k == 0:
            j1.append(f'<rect x="{pxx - 11}" y="{py - 11}" width="22" height="22" rx="3" fill="url(#gold)"/>')
        else:
            j1.append(f'<circle cx="{pxx}" cy="{py}" r="11" fill="url(#gold)"/>')
        j1.append(f'<circle cx="{pxx}" cy="{py}" r="4.6" fill="{t["board1"]}"/>')
        j1.append(f'<text class="mono silk" x="{pxx}" y="94" text-anchor="middle" font-size="14" font-weight="600">{label}</text>')
    j1.append(f'<text class="mono dim" x="930" y="133.5" text-anchor="end" font-size="16" font-weight="700">J1</text>')

    tx_path = "M1012,139 V204 L1048,240 V268"
    sep = f'<tspan fill="{t["cu"]}" dx="10" dy="0"> · </tspan>'
    tag = sep.join(f"<tspan{' dx=\"10\"' if k else ''}>{escape(s)}</tspan>" for k, s in enumerate(TAGLINE))

    css = f"""
    .name{{stroke:url(#goldn);stroke-width:{n(u * 0.46)};stroke-dasharray:1;animation:draw 1.2s cubic-bezier(.65,0,.2,1) both}}
    .nvia{{animation:pop .45s ease-out both}}
    @keyframes draw{{0%{{stroke-dashoffset:1;opacity:0}}6%{{opacity:1}}100%{{stroke-dashoffset:0;opacity:1}}}}
    @keyframes pop{{0%{{opacity:0}}100%{{opacity:1}}}}
    .wave{{fill:none;stroke:{t['sig']};stroke-width:2.6;stroke-linejoin:miter;stroke-dasharray:1;animation:wave 16s linear infinite}}
    @keyframes wave{{0%{{stroke-dashoffset:1;opacity:1}}{draw_end}%{{stroke-dashoffset:0;opacity:1}}{hold_end}%{{stroke-dashoffset:0;opacity:1}}{fade_end}%,100%{{stroke-dashoffset:0;opacity:0}}}}
    .pulse{{fill:none;stroke:{t['sig']};stroke-width:3.4;stroke-linecap:round;stroke-dasharray:.12 1;animation:pulse 2.4s linear infinite}}
    @keyframes pulse{{0%{{stroke-dashoffset:.12}}100%{{stroke-dashoffset:-1}}}}
    .led{{animation:led 1.6s steps(1,end) infinite}}
    @keyframes led{{0%,55%{{opacity:1}}56%,100%{{opacity:.25}}}}
    .guide{{stroke:{t['dim']};stroke-opacity:.35;stroke-width:1;stroke-dasharray:2 4}}
    {''.join(kf)}"""

    body = board(W, H, t) + f"""
  <!-- board furniture -->
  <g>{mount_hole(34, 34, t)}{mount_hole(W - 34, 34, t)}{mount_hole(34, H - 34, t)}{mount_hole(W - 34, H - 34, t)}</g>
  <text class="mono dim" x="64" y="47" font-size="15" letter-spacing="3" font-weight="600">REV {AGE} · BASED IN THE UAE</text>

  <!-- background routing -->
  <g class="bg">
    <path d="M968,139 V178 L942,204 H904"/>
    <path d="M1056,139 V172 L1088,204 H1199"/>
    <path d="M1100,139 V158 L1120,178 H1199"/>
  </g>
  {via(904, 204, t, r=7, hole=2.8)}

  <!-- the handle, routed as traces -->
  <g>
    {name_svg}
  </g>

  <text class="mono silk" x="64" y="243" font-size="23" font-weight="500">{tag}</text>

  <!-- J1: the UART header -->
  <path class="trace" stroke-width="4" d="{tx_path}"/>
  <path class="pulse" pathLength="1" d="{tx_path}"/>
  <g>{''.join(j1)}</g>

  <!-- logic analyzer capture: the line really does spell the handle at 8N1 -->
  <rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" rx="12" fill="{t['panel']}" stroke="{t['panel_edge']}" stroke-width="1.5"/>
  <rect x="1034" y="266" width="28" height="12" rx="3" fill="url(#gold)"/>
  <text class="mono dim" x="{n(x0)}" y="301" font-size="14" letter-spacing="2" font-weight="600">CH1 · UART TX · 115200 8N1</text>
  <circle class="led" cx="{n(x1 - 178)}" cy="296" r="4.5" fill="{t['sig']}"/>
  <text class="mono dim" x="{n(x1)}" y="301" font-size="14" letter-spacing="2" font-weight="600" text-anchor="end">8 BYTES DECODED</text>
  <g class="guide">{''.join(guides)}</g>
  <path class="wave" pathLength="1" d="{d}"/>
  <g>{''.join(boxes)}</g>
"""
    defs = f"""
    <linearGradient id="goldn" gradientUnits="userSpaceOnUse" x1="0" y1="80" x2="0" y2="{80 + 6 * u}">
      <stop offset="0" stop-color="{t['cu0']}"/><stop offset="1" stop-color="{t['cu1']}"/>
    </linearGradient>"""
    return svg(W, H, t, body, css, defs, title=f"{HANDLE}: {', '.join(TAGLINE)}. Based in the UAE.")


# ------------------------------------------------------------------ cards
RAMP = ["#f5c451", "#f59a3a", "#e8603c", "#c2304a", "#7a1f55"]


def ramp(f):
    """Infrared colour ramp, 0 = 0.75 um (starlight), 1 = 5 um (warm dust)."""
    f = max(0.0, min(1.0, f)) * (len(RAMP) - 1)
    i = min(int(f), len(RAMP) - 2)
    a, b, k = RAMP[i], RAMP[i + 1], f - i
    return "#" + "".join(
        f"{round(int(a[j:j + 2], 16) * (1 - k) + int(b[j:j + 2], 16) * k):02x}" for j in (1, 3, 5)
    )


def panel_frame(t, PX, PY, PW, PH, left, right):
    return (
        f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="12" fill="{t["panel"]}" stroke="{t["panel_edge"]}" stroke-width="1.5"/>'
        f'<text class="mono dim" x="{PX + 20}" y="{PY + 27}" font-size="13" letter-spacing="2" font-weight="600">{escape(left)}</text>'
        f'<text class="mono dim" x="{PX + PW - 20}" y="{PY + 27}" font-size="13" letter-spacing="2" font-weight="600" text-anchor="end">{escape(right)}</text>'
    )


def viz_sky(t, PX, PY, PW, PH):
    """All-sky map in a Hammer projection, galactic plane across the middle."""
    cx, cy, A, B = PX + PW / 2, PY + 128, 172, 86
    rng = random.Random(11)

    def proj(lon, lat):
        lam, phi = math.radians(lon), math.radians(lat)
        d = math.sqrt(1 + math.cos(phi) * math.cos(lam / 2))
        return cx - A * math.cos(phi) * math.sin(lam / 2) / d, cy - B * math.sin(phi) / d

    def line(points):
        return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)

    grat = [line([proj(lon, b) for b in range(-90, 91, 6)]) for lon in (-120, -60, 0, 60, 120)]
    grat += [line([proj(lon, lat) for lon in range(-180, 181, 6)]) for lat in (-60, -30, 0, 30, 60)]

    groups = {}
    for _ in range(440):
        r = rng.random()
        if r < 0.52:  # thin disk
            lat = rng.expovariate(1 / 5.5) * rng.choice((-1, 1))
            lon = rng.gauss(0, 58) if rng.random() < 0.7 else rng.uniform(-180, 180)
            col = rng.choice(["#ffe6ad", "#ffc670", "#f79a4a", "#ee7044"])
        elif r < 0.72:  # bulge
            lon, lat = rng.gauss(0, 11), rng.gauss(0, 7)
            col = rng.choice(["#ffe6ad", "#ffc670", "#ffd98a"])
        else:  # halo
            lon, lat = rng.uniform(-180, 180), math.degrees(math.asin(rng.uniform(-1, 1)))
            col = rng.choice(["#ffffff", "#ffe6ad", "#cfe0ff"])
        lon, lat = ((lon + 180) % 360) - 180, max(-88, min(88, lat))
        x, y = proj(lon, lat)
        size, op = 0.45 + 1.5 * rng.random() ** 4, 0.35 + 0.65 * rng.random()
        groups.setdefault(col, []).append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{size:.2f}" opacity="{op:.2f}"/>')
    stars = "".join(f'<g fill="{c}">{"".join(v)}</g>' for c, v in groups.items())

    # reticle on the search example from the project README: 05h35m -05d23m (M42)
    rx, ry = proj(-151.0, -19.4)
    k = 8
    ret = "".join(
        f'<path d="M{rx + sx * k:.1f},{ry + sy * (k - 5):.1f} V{ry + sy * k:.1f} H{rx + sx * (k - 5):.1f}"/>'
        for sx in (-1, 1) for sy in (-1, 1)
    )

    by = PY + PH - 44
    x0 = cx - 145.1
    ticks, labels = [], []
    for d in range(6):
        gx = x0 + d * 49.2
        for c in range(17):
            ticks.append(f'<rect x="{gx + c * 2.6:.1f}" y="{by}" width="1.5" height="11" fill="{ramp((d * 17 + c) / 101)}"/>')
        labels.append(f'<text class="mono dim" x="{gx + 21.6:.1f}" y="{by + 27}" text-anchor="middle" font-size="10.5" letter-spacing="1">D{d + 1}</text>')

    defs = f"""
    <clipPath id="sky"><ellipse cx="{cx}" cy="{cy}" rx="{A}" ry="{B}"/></clipPath>
    <radialGradient id="dust"><stop offset="0" stop-color="#ff9a4a" stop-opacity=".85"/><stop offset=".55" stop-color="#c2304a" stop-opacity=".32"/><stop offset="1" stop-color="#7a1f55" stop-opacity="0"/></radialGradient>
    <radialGradient id="bulge"><stop offset="0" stop-color="#ffe9b8" stop-opacity=".9"/><stop offset="1" stop-color="#ffb14d" stop-opacity="0"/></radialGradient>"""
    css = """
    .stars{opacity:.85;animation:stars 9s ease-in-out infinite alternate}
    .dust{opacity:.55;animation:dust 9s ease-in-out infinite alternate}
    .band{transform:translateX(118px);animation:band 9s ease-in-out infinite alternate}
    @keyframes stars{from{opacity:1}to{opacity:.4}}
    @keyframes dust{from{opacity:.15}to{opacity:1}}
    @keyframes band{from{transform:translateX(0)}to{transform:translateX(288.5px)}}"""
    body = panel_frame(t, PX, PY, PW, PH, "ALL-SKY · 102 BANDS", "0.75 – 5.0 µm") + f"""
  <ellipse cx="{cx}" cy="{cy}" rx="{A}" ry="{B}" fill="#070a11"/>
  <g clip-path="url(#sky)">
    <g class="dust"><ellipse cx="{cx}" cy="{cy}" rx="158" ry="27" fill="url(#dust)"/></g>
    <ellipse cx="{cx}" cy="{cy}" rx="36" ry="24" fill="url(#bulge)" opacity=".8"/>
    <g fill="none" stroke="#fff" stroke-opacity=".13" stroke-width=".8">{''.join(f'<path d="{g}"/>' for g in grat)}</g>
    <g class="stars">{stars}</g>
  </g>
  <ellipse cx="{cx}" cy="{cy}" rx="{A}" ry="{B}" fill="none" stroke="#3a4554" stroke-width="1.5"/>
  <g fill="none" stroke="#4fe3c1" stroke-width="1.6" stroke-linecap="round">{ret}<path d="M{rx - k:.1f},{ry + k:.1f} l-9,9 h-7"/></g>
  <text class="mono" x="{rx - 29:.1f}" y="{ry + 21:.1f}" text-anchor="end" font-size="11.5" font-weight="600" fill="#4fe3c1">M42 · 05h35m −05d23m</text>
  {''.join(ticks)}{''.join(labels)}
  <g class="band"><rect x="{x0 - 3.2:.1f}" y="{by - 4}" width="7.9" height="19" rx="2.5" fill="none" stroke="{t['silk']}" stroke-width="1.6"/></g>
"""
    return defs, css, body


def viz_boot(t, PX, PY, PW, PH):
    """eMMC partition strip, zoomed into the first eight bytes of boot.img."""
    parts = [("sbl1", 38), ("tz", 28), ("aboot", 44), ("boot", 44), ("recovery", 62), ("system", 56), ("userdata", 68)]
    x, y0, out, boot = PX + 20, PY + 46, [], None
    for name, w in parts:
        hot = name == "boot"
        if hot:
            boot = (x, w)
        out.append(
            f'<rect x="{x}" y="{y0}" width="{w}" height="30" rx="4" fill="{t["sig"] if hot else "none"}" fill-opacity="{0.16 if hot else 0}" stroke="{t["sig"] if hot else t["dim"]}" stroke-opacity="{1 if hot else 0.45}" stroke-width="1.3"/>'
            f'<text class="mono {"silk" if hot else "dim"}" x="{x + w / 2}" y="{y0 + 19.5}" text-anchor="middle" font-size="11" font-weight="{700 if hot else 500}">{name}</text>'
        )
        x += w + 4
    bx, bwid = boot
    dy, bw, gap = PY + 110, (PW - 40 - 7 * 5) / 8, 5
    dx0 = PX + 20
    zoom = f"M{bx},{y0 + 30} L{dx0},{dy} H{dx0 + 8 * bw + 7 * gap} L{bx + bwid},{y0 + 30}"
    kf, boxes = [], []
    for i, ch in enumerate("ANDROID!"):
        p = 5 + i * 4.2
        kf.append(f"@keyframes m{i}{{0%,{n(p)}%{{opacity:0}}{n(p + 1.5)}%,88%{{opacity:1}}94%,100%{{opacity:0}}}}.m{i}{{animation:m{i} 11s linear infinite}}")
        bxx = dx0 + i * (bw + gap)
        boxes.append(
            f'<g class="m{i}"><rect x="{n(bxx)}" y="{dy}" width="{n(bw)}" height="44" rx="6" fill="{t["sig"]}" fill-opacity=".10" stroke="{t["sig"]}" stroke-opacity=".5"/>'
            f'<text class="mono silk" x="{n(bxx + bw / 2)}" y="{dy + 20}" text-anchor="middle" font-size="16" font-weight="700">{escape(ch)}</text>'
            f'<text class="mono dim" x="{n(bxx + bw / 2)}" y="{dy + 36}" text-anchor="middle" font-size="11">{ord(ch):02X}</text></g>'
        )
    css = f"""
    .cur{{animation:cur 1.1s steps(1,end) infinite}}
    @keyframes cur{{0%,50%{{opacity:1}}51%,100%{{opacity:0}}}}
    {''.join(kf)}"""
    body = panel_frame(t, PX, PY, PW, PH, "EMMC · 52 PARTITIONS", "EDL 05C6:9008") + f"""
  <path d="{zoom}" fill="{t['sig']}" fill-opacity=".07" stroke="{t['sig']}" stroke-opacity=".45" stroke-width="1" stroke-dasharray="2 3"/>
  {''.join(out)}
  {''.join(boxes)}
  <text class="mono dim" x="{dx0}" y="{dy + 63}" font-size="11" letter-spacing="1.6">BOOT.IMG · FIRST 8 BYTES · MAGIC</text>
  <text class="mono dim" x="{dx0}" y="{PY + PH - 44}" font-size="12.5"><tspan fill="{t['cu']}" font-weight="700">$</tspan> edl.py w boot magisk_patched.img</text>
  <text class="mono sig" x="{dx0}" y="{PY + PH - 20}" font-size="13.5" font-weight="700">uid=0(root) gid=0(root)<tspan class="cur" dx="5">█</tspan></text>
"""
    return "", css, body


def viz_ret(t, PX, PY, PW, PH):
    """The same instruction on both architectures: ret, one byte against four."""
    c, g = 13, 3
    span = 8 * c + 7 * g

    def row(byte, x, y, hot=()):
        out = []
        for i in range(8):
            on, h = (byte >> (7 - i)) & 1, i in hot
            col = t["sig"] if h else t["cu"]
            cx = x + i * (c + g)
            if on:
                out.append(f'<rect x="{cx}" y="{y}" width="{c}" height="{c}" rx="3" fill="{col}"/>')
            else:
                out.append(f'<rect x="{cx + .7}" y="{y + .7}" width="{c - 1.4}" height="{c - 1.4}" rx="2.4" fill="none" stroke="{col if h else t["dim"]}" stroke-opacity="{.95 if h else .45}" stroke-width="1.4"/>')
        out.append(f'<text class="mono silk" x="{x + span + 9}" y="{y + 11}" font-size="12.5" font-weight="700">{byte:02X}</text>')
        return "".join(out)

    lx, rx, top = PX + 20, PX + 232, PY + 72
    word = 0xD65F03C0  # ret: branch to x30, the link register
    rows = []
    for r in range(4):
        hot = [i - 8 * r for i in range(22, 27) if i // 8 == r]  # Rn, bits 9:5
        rows.append(row((word >> (24 - 8 * r)) & 0xFF, rx, top + r * 17, hot))
    name, _ = lettering("ret", lx, top + 30, 5.8, t, gap=1.5, animate=False, cls="rl", via_cls="tvia", via_r=0.52, hole_r=0.2)
    ay = top + c / 2
    css = f"""
    .rl{{stroke:{t['cu']};stroke-width:3.4}}
    .cur{{animation:cur 1.1s steps(1,end) infinite}}
    @keyframes cur{{0%,50%{{opacity:1}}51%,100%{{opacity:0}}}}"""
    body = panel_frame(t, PX, PY, PW, PH, "ENCODING", "X86 → ARM64") + f"""
  <text class="mono dim" x="{lx}" y="{top - 13}" font-size="12"><tspan class="silk" font-weight="700">x86</tspan> · 1 byte</text>
  {row(0xC3, lx, top)}
  <g>{name}</g>
  <path d="M{lx + span + 40},{ay} H{rx - 14} m-7,-6 l7,6 l-7,6" fill="none" stroke="{t['dim']}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
  <text class="mono dim" x="{rx}" y="{top - 13}" font-size="12"><tspan class="silk" font-weight="700">arm64</tspan> · 4 bytes</text>
  {''.join(rows)}
  <rect x="{rx}" y="{top + 79}" width="9" height="9" rx="2" fill="{t['sig']}"/>
  <text class="mono sig" x="{rx + 16}" y="{top + 88}" font-size="11.5" font-weight="700">Rn = x30 (lr)</text>
  <text class="mono dim" x="{lx}" y="{PY + PH - 44}" font-size="12.5"><tspan fill="{t['cu']}" font-weight="700">$</tspan> file RobloxPlayer</text>
  <text class="mono sig" x="{lx}" y="{PY + PH - 20}" font-size="13.5" font-weight="700">Mach-O 64-bit executable arm64<tspan class="cur" dx="5">█</tspan></text>
"""
    return "", css, body


VIZ = {"sky": viz_sky, "boot": viz_boot, "ret": viz_ret}


def card(p, t, idx):
    H = 334
    PX, PY, PW, PH = 744, 36, 404, 262
    u, tx, top = 7, 56, 78
    title, tw = lettering(p["title"], tx, top, u, t, gap=1.5, animate=False, cls="ttl", via_cls="tvia", via_r=0.56, hole_r=0.21)
    ax = tx + tw + 2.6 * u
    arrow = (
        f'<path class="trace ttl" d="M{n(ax)},{n(top + 6 * u)} L{n(ax + 4 * u)},{n(top + 2 * u)}"/>'
        f'<path class="trace ttl" d="M{n(ax + 1.4 * u)},{n(top + 2 * u)} H{n(ax + 4 * u)} V{n(top + 4.6 * u)}"/>'
        + via(ax, top + 6 * u, t, r=u * 0.56, hole=u * 0.21)
    )
    desc = "".join(
        f'<text class="sans" x="{tx}" y="{178 + 29 * k}" font-size="20" fill="{t["desc"]}">{escape(line)}</text>'
        for k, line in enumerate(p["desc"])
    )
    pads, x, sy = [], tx + 7, H - 52
    for s in p["stack"]:
        pads.append(via(x, sy, t, r=6.5, hole=2.6))
        pads.append(f'<text class="mono dim" x="{n(x + 15)}" y="{sy + 5}" font-size="14" letter-spacing="1.6" font-weight="600">{escape(s.upper())}</text>')
        x += 15 + len(s) * 10.3 + 28
    feed = f"M676,{sy} H692 L712,{sy - 20} H{PX}"
    defs, vcss, viz = VIZ[p["viz"]](t, PX, PY, PW, PH)
    defs += f"""
    <linearGradient id="goldt" gradientUnits="userSpaceOnUse" x1="0" y1="{top}" x2="0" y2="{top + 8 * u}">
      <stop offset="0" stop-color="{t['cu0']}"/><stop offset="1" stop-color="{t['cu1']}"/>
    </linearGradient>"""
    css = f"""
    .ttl{{stroke:url(#goldt);stroke-width:{n(u * 0.62)}}}
    .pulse{{fill:none;stroke:{t['sig']};stroke-width:3.2;stroke-linecap:round;stroke-dasharray:.16 1;stroke-dashoffset:.16;animation:pulse 2.6s linear infinite}}
    @keyframes pulse{{0%{{stroke-dashoffset:.16}}100%{{stroke-dashoffset:-1}}}}{vcss}"""
    body = board(W, H, t, rx=20) + f"""
  <g fill="none" stroke="{t['dim']}" stroke-opacity=".5"><circle cx="30" cy="30" r="8"/><circle cx="30" cy="{H - 30}" r="8"/></g>
  <g fill="{t['cu']}"><circle cx="30" cy="30" r="3.2"/><circle cx="30" cy="{H - 30}" r="3.2"/></g>
  <text class="mono dim" x="{tx}" y="52" font-size="14" letter-spacing="2.6" font-weight="600"><tspan class="cu">P{idx}</tspan> · {escape(p['meta'])}</text>
  <g>
    {title}
    {arrow}
  </g>
  {desc}
  <g>{''.join(pads)}</g>
  <path class="trace" stroke-width="3.6" d="{feed}"/>
  <path class="pulse" pathLength="1" d="{feed}"/>
  {via(676, sy, t, r=6.5, hole=2.6)}
  {viz}
  <rect x="{PX - 6}" y="{sy - 27}" width="12" height="14" rx="3" fill="url(#gold)"/>
"""
    return svg(W, H, t, body, css, defs, title=f"{p['title']}: {' '.join(p['desc'])}")


# ---------------------------------------------------------------- toolkit
def toolkit(t):
    H = 430
    bx0, bx1 = 490, 710
    ys = [136 + 34 * k for k in range(6)]
    by0, by1 = ys[0] - 30, ys[-1] + 30
    mid, cy = (bx0 + bx1) // 2, (by0 + by1) / 2
    out, pulses, nums = [], [], []
    for k, y in enumerate(ys):
        ly = cy + (k - 2.5) * 46
        d = ly - y
        for side, labels in ((-1, PINS_LEFT), (1, PINS_RIGHT)):
            edge = bx0 if side < 0 else bx1
            px, bend, end = edge + side * 18, edge + side * 52, edge + side * 124
            num = k + 1 if side < 0 else 12 - k
            path = f"M{px},{y} H{bend} L{n(bend + side * abs(d))},{n(ly)} H{end}"
            out.append(f'<rect x="{min(edge, px)}" y="{y - 4}" width="18" height="8" fill="{t["lead"]}"/>')
            out.append(f'<path class="trace" stroke-width="3.2" d="{path}"/>')
            pulses.append(f'<path class="pulse" pathLength="1" style="animation-delay:{n((k if side < 0 else 11 - k) * 0.5)}s" d="{path}"/>')
            if num == 1:
                out.append(f'<rect x="{px - 10}" y="{y - 10}" width="20" height="20" rx="3" fill="url(#gold)"/><circle cx="{px}" cy="{y}" r="4" fill="{t["board1"]}"/>')
            else:
                out.append(via(px, y, t, r=10, hole=4))
            out.append(via(end, ly, t, r=6.5, hole=2.6))
            out.append(
                f'<text class="mono silk" x="{end + side * 18}" y="{n(ly + 7.5)}" font-size="22" font-weight="500" text-anchor="{"end" if side < 0 else "start"}">{escape(labels[k])}</text>'
            )
            nums.append(
                f'<text class="mono" x="{edge - side * 13}" y="{y + 4.5}" font-size="12.5" fill="{t["chip_dim"]}" text-anchor="{"start" if side < 0 else "end"}">{num}</text>'
            )
    top_label = cy - 2.5 * 46 - 36
    css = f"""
    .pulse{{fill:none;stroke:{t['sig']};stroke-width:3;stroke-linecap:round;stroke-dasharray:.14 1;stroke-dashoffset:.14;animation:pulse 6s linear infinite}}
    @keyframes pulse{{0%{{stroke-dashoffset:.14}}40%,100%{{stroke-dashoffset:-1}}}}"""
    defs = f"""
    <linearGradient id="pkg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{t['chip0']}"/><stop offset="1" stop-color="{t['chip']}"/>
    </linearGradient>"""
    body = board(W, H, t) + f"""
  <g>{mount_hole(34, 34, t)}{mount_hole(W - 34, 34, t)}{mount_hole(34, H - 34, t)}{mount_hole(W - 34, H - 34, t)}</g>
  <text class="mono cu" x="{bx0 - 142}" y="{n(top_label)}" text-anchor="end" font-size="14" letter-spacing="2.6" font-weight="600">RECON + REVERSING</text>
  <text class="mono cu" x="{bx1 + 142}" y="{n(top_label)}" font-size="14" letter-spacing="2.6" font-weight="600">BUILD + RUN</text>

  <!-- silkscreen courtyard and designator -->
  <rect x="{bx0 - 36}" y="{by0 - 10}" width="{bx1 - bx0 + 72}" height="{by1 - by0 + 20}" rx="6" fill="none" stroke="{t['silk']}" stroke-opacity=".55" stroke-width="1.5" stroke-dasharray="1 0"/>
  <path d="M{bx0 - 36},{by0 - 18} h12 l-12,12 z" fill="{t['silk']}" fill-opacity=".7" transform="translate(-10 0)"/>
  <text class="mono dim" x="{bx1 + 36}" y="{by0 - 18}" text-anchor="end" font-size="14" font-weight="700" letter-spacing="1">U1</text>

  {''.join(out)}
  {''.join(pulses)}

  <!-- package -->
  <rect x="{bx0}" y="{by0}" width="{bx1 - bx0}" height="{by1 - by0}" rx="9" fill="url(#pkg)" stroke="{t['chip_edge']}" stroke-width="2"/>
  <rect x="{bx0 + 6}" y="{by0 + 6}" width="{bx1 - bx0 - 12}" height="{by1 - by0 - 12}" rx="5" fill="none" stroke="#fff" stroke-opacity=".06" stroke-width="1.2"/>
  <path d="M{mid - 15},{by0} a15,15 0 0 0 30,0" fill="#000" fill-opacity=".45" stroke="{t['chip_edge']}" stroke-width="2"/>
  <circle cx="{bx0 + 36}" cy="{by0 + 18}" r="4.5" fill="#000" fill-opacity=".4" stroke="{t['chip_dim']}" stroke-opacity=".5"/>
  {''.join(nums)}
  <text class="mono" x="{mid}" y="{n(cy + 2)}" text-anchor="middle" font-size="32" font-weight="700" fill="{t['chip_text']}">3CH0-{AGE}</text>
  <text class="mono" x="{mid}" y="{n(cy + 30)}" text-anchor="middle" font-size="13" letter-spacing="5" fill="{t['chip_dim']}">TOOLKIT</text>
  <text class="mono" x="{mid}" y="{n(cy + 56)}" text-anchor="middle" font-size="12" letter-spacing="3" fill="{t['chip_dim']}" fill-opacity=".8">UAE {DATE_CODE}</text>

  <text class="mono dim" x="600" y="{H - 30}" text-anchor="middle" font-size="12.5" letter-spacing="3" font-weight="600">FIG. 1 · PIN CONFIGURATION · TOP VIEW</text>
"""
    alt = "Toolkit pinout. " + ", ".join(PINS_LEFT + PINS_RIGHT) + "."
    return svg(W, H, t, body, css, defs, title=alt)


# ---------------------------------------------------- headers and footer
def header(label, t):
    """Section label followed by a three-trace bus with a 45 degree jog."""
    H, y0, s = 78, 40, 9
    start = 2 + len(label) * 17.4 + 34
    jog, rise = 930, 16
    out = []
    for k in range(3):
        y = y0 + k * s
        xj = jog + k * s * 0.414
        xa, xb = start + (2 - k) * 15, W - 12 - (2 - k) * 15
        out.append(f'<path class="trace" stroke-width="2.6" d="M{n(xa)},{y} H{n(xj)} L{n(xj + rise)},{y - rise} H{n(xb)}"/>')
        out.append(via(xa, y, t, r=5.5, hole=2.2) + via(xb, y - rise, t, r=5.5, hole=2.2))
    body = f"""  <text class="mono" x="2" y="{y0 + s + 7}" font-size="20" font-weight="700" letter-spacing="5" fill="{t['page_ink']}">{escape(label)}</text>
  {''.join(out)}
"""
    return svg(W, H, t, body, title=label.title())


def footer(t):
    """The capture ends the way a transmission should: 0x04, EOT."""
    H, hi, lo, bw = 96, 20, 44, 17
    bits = [0] + [(0x04 >> k) & 1 for k in range(8)] + [1]
    xs = 600 - 5 * bw
    d, level, length = f"M14,{hi} H{xs}", 1, xs - 14.0
    for k, b in enumerate(bits):
        if b != level:
            d += f" V{hi if b else lo}"
            length += lo - hi
            level = b
        d += f" H{xs + (k + 1) * bw}"
        length += bw
    frame_end = length
    d += f" H{W - 14}"
    length += W - 14 - (xs + 10 * bw)
    p = 40 * frame_end / length
    css = f"""
    .wave{{fill:none;stroke:{t['sig']};stroke-width:2.6;stroke-linejoin:miter;stroke-dasharray:1;animation:wave 12s linear infinite}}
    @keyframes wave{{0%{{stroke-dashoffset:1;opacity:1}}40%,88%{{stroke-dashoffset:0;opacity:1}}94%,100%{{stroke-dashoffset:0;opacity:0}}}}
    .eot{{animation:eot 12s linear infinite}}
    @keyframes eot{{0%,{n(p)}%{{opacity:0}}{n(p + 1.5)}%,88%{{opacity:1}}94%,100%{{opacity:0}}}}
    .guide{{stroke:{t['page_dim']};stroke-opacity:.4;stroke-width:1;stroke-dasharray:2 4}}"""
    body = f"""  <g class="guide"><path d="M{xs},12 V52"/><path d="M{xs + 10 * bw},12 V52"/></g>
  <path class="wave" pathLength="1" d="{d}"/>
  <g class="eot"><rect x="{xs + 3}" y="60" width="{10 * bw - 6}" height="28" rx="6" fill="{t['sig']}" fill-opacity=".10" stroke="{t['sig']}" stroke-opacity=".5"/>
  <text class="mono" x="600" y="79.5" text-anchor="middle" font-size="15"><tspan fill="{t['page_dim']}">0x04</tspan><tspan fill="{t['page_ink']}" font-weight="700" dx="10">EOT</tspan></text></g>
"""
    return svg(W, H, t, body, css, title="0x04, end of transmission")


def main():
    out = Path(__file__).resolve().parent.parent / "assets"
    out.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        files = {
            "hero": hero(t),
            "toolkit": toolkit(t),
            "h-work": header("FEATURED WORK", t),
            "h-toolkit": header("TOOLKIT", t),
            "footer": footer(t),
        }
        for i, p in enumerate(PROJECTS, 1):
            files[f"card-{p['slug']}"] = card(p, t, i)
        for stem, content in files.items():
            (out / f"{stem}-{name}.svg").write_text(content)
    print(f"wrote {len(files) * 2} files to {out}")


if __name__ == "__main__":
    main()
