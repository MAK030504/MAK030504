#!/usr/bin/env python3
"""Neofetch-style card. The lines fade in once and then hold."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "info-card.svg"

BG = "#0d1117"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
ACCENT = "#3fb950"

LINES = [
    ("now", "Computer engineering, GIKI"),
    ("years", "2023 – 2027"),
    ("focus", "Health ML, campus products, hardware"),
    ("stack", "Python, TypeScript, FastAPI"),
    ("", "Next.js, TinyML, Vivado"),
    ("place", "Topi, Pakistan"),
]


def render(static: bool = False) -> str:
    width = 640
    row_h = 32
    top = 78
    height = top + len(LINES) * row_h + 28
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        f'<rect width="{width}" height="{height}" rx="12" fill="{BG}"/>',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="none" stroke="{FRAME}"/>',
        '<circle cx="22" cy="17" r="5" fill="#ff5f56"/>',
        '<circle cx="38" cy="17" r="5" fill="#ffbd2e"/>',
        '<circle cx="54" cy="17" r="5" fill="#27c93f"/>',
        f'<text x="{width / 2}" y="21" fill="{MUTED}" font-size="12" text-anchor="middle">'
        "mak@github ~ $ neofetch</text>",
        f'<line x1="0" y1="34" x2="{width}" y2="34" stroke="{FRAME}"/>',
        f'<text x="24" y="60" fill="{ACCENT}" font-size="16" font-weight="700">mak@giki</text>',
        f'<text x="24" y="72" fill="{ACCENT}" font-size="8">{"─" * 18}</text>',
    ]
    for index, (key, value) in enumerate(LINES):
        y = top + 16 + index * row_h
        delay = 0.25 + index * 0.16
        text = (
            f'<text x="24" y="{y}" fill="{ACCENT}" font-size="15">{key}</text>'
            f'<text x="108" y="{y}" fill="{INK}" font-size="15">{value}</text>'
        )
        if static:
            parts.append(text)
            continue
        parts.append(
            f'<g opacity="0">{text}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.35s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 8" to="0 0" '
            f'begin="{delay:.2f}s" dur="0.35s" fill="freeze"/>'
            f"</g>"
        )
    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    svg = render(static=bool(os.environ.get("STATIC")))
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
