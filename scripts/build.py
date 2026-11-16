#!/usr/bin/env python3
"""Builds the SVG artwork for the profile README.

Run `python3 scripts/build.py` from the repo root. Every asset is written
twice (dark and light) into assets/ and picked by GitHub with <picture>.

Edit the data at the top (AGE, HANDLE, PROJECTS, PINS) and rebuild.
"""
from pathlib import Path
from xml.sax.saxutils import escape

HANDLE = "3ch0less"
AGE = 18
TAGLINE = ["IoT pentesting", "hardware hacking", "AI", "security"]

PROJECTS = [
    dict(
        slug="lumasphere",
        art="sphere",
        meta="NASA SPACE APPS CHALLENGE 2026 · UNIVERSITY OF DUBAI",
        title="Lumasphere",
        desc=[
            "The whole sky in infrared. Step inside NASA SPHEREx's all-sky map, tune",
            "through 102 infrared colors, and watch any patch of sky change over time.",
        ],
        tags=["Python", "FastAPI", "astropy", "JavaScript", "Docker"],
    ),
    dict(
        slug="pvg100e-root",
        art="phone",
        meta="ANDROID · QUALCOMM EDL · REVERSE ENGINEERING",
        title="pvg100e-root",
        desc=[
            "Rooting the Palm Phone through Qualcomm EDL and Magisk, locked bootloader",
            "and all. A full guide, a patched edl tool, and backup and restore scripts.",
        ],
        tags=["Python", "EDL / Firehose", "Magisk", "MSM8937"],
    ),
    dict(
        slug="roblox-2016-arm64",
        art="chip",
        meta="C++ · PORTING · APPLE SILICON",
        title="roblox-2016-arm64",
        desc=[
            "The 2016 Roblox client ported to run natively on Apple Silicon. ARM64",
            "build, GLSL shaders, and offline play working on modern macOS.",
        ],
        tags=["C++", "ARM64", "macOS", "GLSL"],
    ),
]

PINS_LEFT = ["Ghidra", "radare2", "Wireshark", "nmap", "tcpdump", "Burp Suite"]
PINS_RIGHT = ["Python", "C / C++", "JavaScript / TypeScript", "Linux", "Docker", "Android"]

THEMES = {
    "dark": dict(
        board0="#0d1016", board1="#07090c", edge="#262d37", grid="#1b212b",
        panel="#05070a", panel_edge="#1f2630",
        cu0="#f3c876", cu1="#c88a2a", cu="#dba545", cu_dim="#dba545", cu_dim_op="0.30",
        silk="#eef1f5", dim="#8a94a3", sig="#4fe3c1", hole="#0d1117",
        chip="#141920", chip_edge="#2c3440", chip_text="#eef1f5", chip_dim="#7d8796",
        page_ink="#e6edf3", page_dim="#7d8590",
    ),
    "light": dict(
        board0="#fdfcf9", board1="#f3f1ea", edge="#d6d1c4", grid="#e3dfd3",
        panel="#ffffff", panel_edge="#ddd8cb",
        cu0="#c4912f", cu1="#99690f", cu="#a8771a", cu_dim="#a8771a", cu_dim_op="0.38",
        silk="#14181d", dim="#5b6470", sig="#0a8a72", hole="#ffffff",
        chip="#1a1f26", chip_edge="#1a1f26", chip_text="#f2f4f7", chip_dim="#98a1ae",
        page_ink="#1f2328", page_dim="#656d76",
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
}


def lettering(text, x, y, u, t, gap=1.6, animate=True):
    """Returns (svg, width). x,y is the top-left of the cap height."""
    out, cx, i = [], x, 0
    for ch in text:
        gw, strokes, vias = GLYPHS[ch]
        for s in strokes:
            p = [(cx + px * u, y + py * u) for px, py in s]
            closed = s[0] == s[-1]
            d = "M" + " L".join(f"{n(a)},{n(b)}" for a, b in (p[:-1] if closed else p)) + ("Z" if closed else "")
            style = f' style="animation-delay:{n(0.15 + i * 0.07)}s"' if animate else ""
            out.append(f'<path class="trace name" pathLength="1" d="{d}"{style}/>')
            i += 1
        for vx, vy in vias:
            style = f' style="animation-delay:{n(0.75 + i * 0.07)}s"' if animate else ""
            out.append(
                f'<g class="nvia"{style}><circle cx="{n(cx + vx * u)}" cy="{n(y + vy * u)}" r="{n(u * 0.43)}" fill="url(#gold)"/>'
                f'<circle cx="{n(cx + vx * u)}" cy="{n(y + vy * u)}" r="{n(u * 0.17)}" fill="{t["board1"]}"/></g>'
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
def art_sphere(cx, cy, t):
    r = 80
    lat = "".join(f'<path d="M{cx - r},{cy + dy} H{cx + r}"/>' for dy in (-54, -28, 0, 28, 54))
    mer = "".join(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{r}"/>' for rx in (26, 54))
    stars = "".join(
        f'<circle cx="{cx + dx}" cy="{cy + dy}" r="{rr}"/>'
        for dx, dy, rr in [(-38, -30, 2.2), (22, -48, 1.6), (44, 6, 2.6), (-12, 34, 1.8), (-52, 12, 1.4), (10, -8, 3), (30, 46, 1.5)]
    )
    return f"""
    <radialGradient id="ir" cx="42%" cy="38%" r="70%">
      <stop offset="0" stop-color="#ffd98a"/><stop offset=".35" stop-color="#f08a3c"/>
      <stop offset=".7" stop-color="#a92c33"/><stop offset="1" stop-color="#35102c"/>
    </radialGradient>
    <clipPath id="ball"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>""", f"""
  <ellipse cx="{cx}" cy="{cy}" rx="104" ry="30" transform="rotate(-24 {cx} {cy})" fill="none" stroke="{t['cu']}" stroke-opacity=".55" stroke-width="2"/>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#ir)"/>
  <g clip-path="url(#ball)" fill="none" stroke="#fff" stroke-opacity=".28" stroke-width="1.4">{lat}{mer}<path d="M{cx},{cy - r} V{cy + r}"/></g>
  <g clip-path="url(#ball)" fill="#fff" fill-opacity=".92">{stars}</g>
  <path d="M{cx - 95},{cy + 42.3} A104,30 -24 0 0 {cx + 95},{cy - 42.3}" fill="none" stroke="{t['cu']}" stroke-width="2.4" stroke-linecap="round"/>
  <circle cx="{cx + 95}" cy="{cy - 42.3}" r="5.5" fill="{t['silk']}"/>
"""


def art_phone(cx, cy, t):
    w, h = 96, 156
    x, y = cx - w / 2, cy - h / 2 - 6
    return "", f"""
  <path class="trace" stroke-width="4" d="M{cx},{y + h} V{cy + 92} L{cx - 20},{cy + 112} H{cx - 100}"/>
  <rect x="{n(x)}" y="{n(y)}" width="{w}" height="{h}" rx="20" fill="{t['chip']}" stroke="{t['silk']}" stroke-width="3"/>
  <rect x="{n(x + 9)}" y="{n(y + 16)}" width="{w - 18}" height="{h - 34}" rx="8" fill="{t['panel'] if t is THEMES['dark'] else '#0d1117'}"/>
  <circle cx="{cx}" cy="{n(y + 8.5)}" r="2.4" fill="{t['chip_dim']}"/>
  <text class="mono" x="{n(x + 17)}" y="{n(y + 44)}" font-size="13" fill="#7d8796">pepito:/</text>
  <text class="mono" x="{n(x + 17)}" y="{n(y + 76)}" font-size="30" font-weight="700" fill="#4fe3c1">#</text>
  <rect class="cur" x="{n(x + 41)}" y="{n(y + 53)}" width="13" height="26" fill="#4fe3c1"/>
  <rect x="{cx - 9}" y="{n(y + h - 3)}" width="18" height="8" rx="2" fill="url(#gold)"/>
"""


def art_chip(cx, cy, t):
    s = 112
    x, y = cx - s / 2, cy - s / 2
    pins = []
    for k in range(6):
        o = 16 + k * 16
        pins += [
            f'<path d="M{n(x + o)},{n(y)} v-18"/>', f'<path d="M{n(x + o)},{n(y + s)} v18"/>',
            f'<path d="M{n(x)},{n(y + o)} h-18"/>', f'<path d="M{n(x + s)},{n(y + o)} h18"/>',
        ]
    return "", f"""
  <g fill="none" stroke="{t['cu']}" stroke-width="5" stroke-linecap="round">{''.join(pins)}</g>
  <rect x="{n(x)}" y="{n(y)}" width="{s}" height="{s}" rx="12" fill="{t['chip']}" stroke="{t['chip_edge']}" stroke-width="2"/>
  <circle cx="{n(x + 16)}" cy="{n(y + 16)}" r="4.5" fill="{t['chip_dim']}"/>
  <text class="mono" x="{cx}" y="{cy + 6}" text-anchor="middle" font-size="24" font-weight="700" fill="{t['chip_text']}">arm64</text>
  <text class="mono" x="{cx}" y="{cy + 30}" text-anchor="middle" font-size="12" letter-spacing="2" fill="{t['chip_dim']}">NATIVE</text>
"""


ART = {"sphere": art_sphere, "phone": art_phone, "chip": art_chip}


def card(p, t, idx):
    H = 252
    defs, art = ART[p["art"]](140, H // 2, t)
    tx = 290
    chips, x = [], tx
    for tag in p["tags"]:
        w = len(tag) * 9.6 + 26
        chips.append(
            f'<rect x="{n(x)}" y="196" width="{n(w)}" height="30" rx="15" fill="none" stroke="{t["edge"]}" stroke-width="1.5"/>'
            f'<text class="mono dim" x="{n(x + w / 2)}" y="216" text-anchor="middle" font-size="15">{escape(tag)}</text>'
        )
        x += w + 10
    desc = "".join(
        f'<text class="sans dim" x="{tx}" y="{142 + 30 * k}" font-size="21">{escape(line)}</text>'
        for k, line in enumerate(p["desc"])
    )
    css = """
    .cur{animation:cur 1.1s steps(1,end) infinite}
    @keyframes cur{0%,50%{opacity:1}51%,100%{opacity:0}}"""
    body = board(W, H, t, rx=20) + f"""
  <text class="mono dim" x="{W - 40}" y="47" text-anchor="end" font-size="14" letter-spacing="2" font-weight="600">P{idx}</text>
  {art}
  <text class="mono cu" x="{tx}" y="56" font-size="15" letter-spacing="2.4" font-weight="600">{escape(p['meta'])}</text>
  <text class="mono silk" x="{tx}" y="104" font-size="40" font-weight="700">{escape(p['title'])}</text>
  {desc}
  <g>{''.join(chips)}</g>
  <g transform="translate({W - 74},186)" fill="none" stroke="{t['cu']}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="20" cy="20" r="20" stroke-opacity=".5" stroke-width="1.5"/>
    <path d="M13,27 L27,13 M16,13 H27 V24"/>
  </g>
"""
    return svg(W, H, t, body, css, defs, title=f"{p['title']}: {' '.join(p['desc'])}")


# ---------------------------------------------------------------- toolkit
def toolkit(t):
    H = 392
    cx0, cx1, cy0, cy1 = 462, 738, 64, 348
    rows = [cy0 + 34 + k * 43.2 for k in range(6)]
    out = []
    for k, y in enumerate(rows):
        for side, labels in ((-1, PINS_LEFT), (1, PINS_RIGHT)):
            edge = cx0 if side < 0 else cx1
            num = k + 1 if side < 0 else 12 - k
            pin_x = edge - 36 if side < 0 else edge
            out.append(f'<rect x="{pin_x}" y="{n(y - 9)}" width="36" height="18" rx="3" fill="url(#gold)"/>')
            out.append(f'<path class="trace" stroke-width="3" d="M{edge + side * 36},{n(y)} H{edge + side * 86}"/>')
            out.append(via(edge + side * 90, y, t, r=6.5, hole=2.6))
            out.append(
                f'<text class="mono silk" x="{edge + side * 110}" y="{n(y + 7.5)}" font-size="22" font-weight="500" text-anchor="{"end" if side < 0 else "start"}">{escape(labels[k])}</text>'
            )
            out.append(
                f'<text class="mono" x="{edge - side * 16}" y="{n(y + 5)}" font-size="14" fill="{t["chip_dim"]}" text-anchor="{"start" if side < 0 else "end"}">{num}</text>'
            )
    mid = (cx0 + cx1) // 2
    body = board(W, H, t) + f"""
  <text class="mono cu" x="{cx0 - 110}" y="50" text-anchor="end" font-size="14" letter-spacing="2.4" font-weight="600">RECON + REVERSING</text>
  <text class="mono cu" x="{cx1 + 110}" y="50" font-size="14" letter-spacing="2.4" font-weight="600">BUILD + RUN</text>
  <rect x="{cx0}" y="{cy0}" width="{cx1 - cx0}" height="{cy1 - cy0}" rx="12" fill="{t['chip']}" stroke="{t['chip_edge']}" stroke-width="2"/>
  <path d="M{mid - 20},{cy0} a20,20 0 0 0 40,0" fill="{t['board1']}" stroke="{t['chip_edge']}" stroke-width="2"/>
  <circle cx="{cx0 + 44}" cy="{cy0 + 16}" r="4" fill="{t['chip_dim']}"/>
  <text class="mono" x="{mid}" y="{(cy0 + cy1) // 2 + 4}" text-anchor="middle" font-size="34" font-weight="700" fill="{t['chip_text']}">3CH0-{AGE}</text>
  <text class="mono" x="{mid}" y="{(cy0 + cy1) // 2 + 34}" text-anchor="middle" font-size="14" letter-spacing="5" fill="{t['chip_dim']}">TOOLKIT</text>
  {''.join(out)}
"""
    alt = "Toolkit pinout. " + ", ".join(PINS_LEFT + PINS_RIGHT) + "."
    return svg(W, H, t, body, title=alt)


# ---------------------------------------------------- headers and footer
def header(num, label, t):
    H, y = 84, 26  # extra room on top so sections breathe without <br> hacks
    start = 62 + len(label) * 18.2 + 26
    body = f"""  <text class="mono" x="2" y="{y + 37}" font-size="22" font-weight="700" fill="{t['cu']}">{num}</text>
  <text class="mono" x="46" y="{y + 37}" font-size="22" font-weight="700" letter-spacing="4" fill="{t['page_ink']}">{escape(label)}</text>
  <path class="trace" stroke-width="3" d="M{n(start)},{y + 30} H{W - 60} L{W - 44},{y + 14} H{W - 16}"/>
  {via(start, y + 30, t, r=7, hole=2.8)}{via(W - 12, y + 14, t, r=7, hole=2.8)}
"""
    return svg(W, H, t, body, title=label.title())


def footer(t):
    H = 48
    body = f"""  <path class="trace" stroke-width="3" d="M16,24 H430"/><path class="trace" stroke-width="3" d="M770,24 H{W - 16}"/>
  {via(12, 24, t, r=7, hole=2.8)}{via(434, 24, t, r=7, hole=2.8)}{via(766, 24, t, r=7, hole=2.8)}{via(W - 12, 24, t, r=7, hole=2.8)}
  <text class="mono" x="600" y="30" text-anchor="middle" font-size="16" font-weight="600" letter-spacing="4" fill="{t['page_dim']}">END OF TRANSMISSION</text>
"""
    return svg(W, H, t, body, title="End of transmission")


def main():
    out = Path(__file__).resolve().parent.parent / "assets"
    out.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        files = {
            "hero": hero(t),
            "toolkit": toolkit(t),
            "h-work": header("01", "FEATURED WORK", t),
            "h-toolkit": header("02", "TOOLKIT", t),
            "footer": footer(t),
        }
        for i, p in enumerate(PROJECTS, 1):
            files[f"card-{p['slug']}"] = card(p, t, i)
        for stem, content in files.items():
            (out / f"{stem}-{name}.svg").write_text(content)
    print(f"wrote {len(files) * 2} files to {out}")


if __name__ == "__main__":
    main()
