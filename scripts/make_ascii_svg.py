#!/usr/bin/env python3
"""Build the typing monogram SVG, or convert a prepped photo when one exists.

The portrait prints once, top to bottom, and then holds. GitHub plays the
SMIL animation inside an <img> and ignores JavaScript.
"""

from __future__ import annotations

import html
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mak-ascii.svg"
PREPPED = ROOT / "source-prepped.png"

BG = "#0d1117"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
RAMP = " .`:-=+*cs#%@"

# Block letters. A photo at source-prepped.png replaces this grid.
_GLYPHS = {
    "M": [
        "##      ##",
        "###    ###",
        "####  ####",
        "## #### ##",
        "##  ##  ##",
        "##      ##",
        "##      ##",
    ],
    "A": [
        "  ######  ",
        " ##    ## ",
        "##      ##",
        "##########",
        "##      ##",
        "##      ##",
        "##      ##",
    ],
    "K": [
        "##      ##",
        "##    ##  ",
        "##  ##    ",
        "####      ",
        "##  ##    ",
        "##    ##  ",
        "##      ##",
    ],
}


def monogram_rows() -> list[str]:
    gap = "   "
    width = len(_GLYPHS["M"][0])
    for glyph in _GLYPHS.values():
        if any(len(row) != width for row in glyph):
            raise ValueError("monogram glyphs must share one width")
    body = [gap.join(_GLYPHS[char][row] for char in "MAK") for row in range(7)]
    width = max(len(line) for line in body)
    centered = [line.center(width) for line in body]
    margin = " " * width
    return [margin, *centered, margin]


def rows_from_image(path: Path) -> list[str]:
    from PIL import Image, ImageEnhance

    columns = int(os.environ.get("COLS", "72"))
    image = Image.open(path).convert("L")
    image = ImageEnhance.Contrast(image).enhance(1.2)
    rows = max(8, round(columns * image.height / image.width * 0.55))
    image = image.resize((columns, rows), Image.Resampling.LANCZOS)
    pixels = image.load()
    lines: list[str] = []
    for y in range(rows):
        chars = []
        for x in range(columns):
            lum = pixels[x, y] / 255
            if lum >= 0.82:
                chars.append(" ")
                continue
            index = round((1 - lum) * (len(RAMP) - 1))
            chars.append(RAMP[max(0, min(len(RAMP) - 1, index))])
        lines.append("".join(chars))
    return lines


def render(lines: list[str], static: bool = False) -> str:
    columns = max(len(line) for line in lines)
    lines = [line.ljust(columns) for line in lines]
    font_size = 18
    char_w = font_size * 0.62
    pad = 26
    art_w = columns * char_w
    width = art_w + pad * 2
    cell_h = 24
    art_h = len(lines) * cell_h
    title_h = 40
    height = title_h + art_h + 46
    row_dur = 4.8 / max(len(lines), 1)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        f'<rect width="{width:.0f}" height="{height:.0f}" rx="12" fill="{BG}"/>',
        f'<rect x="0.5" y="0.5" width="{width - 1:.0f}" height="{height - 1:.0f}" rx="12" fill="none" stroke="{FRAME}"/>',
        '<circle cx="22" cy="17" r="5" fill="#ff5f56"/>',
        '<circle cx="38" cy="17" r="5" fill="#ffbd2e"/>',
        '<circle cx="54" cy="17" r="5" fill="#27c93f"/>',
        f'<text x="{width / 2:.0f}" y="22" fill="{MUTED}" font-size="13" text-anchor="middle">portrait.sh</text>',
        f'<line x1="0" y1="{title_h}" x2="{width:.0f}" y2="{title_h}" stroke="{FRAME}"/>',
    ]
    for index, line in enumerate(lines):
        y = title_h + 8 + index * cell_h + cell_h * 0.78
        row_y = title_h + 6 + index * cell_h
        text = (
            f'<text xml:space="preserve" x="{pad}" y="{y:.1f}" fill="{INK}" font-size="{font_size}">'
            f'{html.escape(line)}</text>'
        )
        if static:
            parts.append(text)
            continue
        delay = index * row_dur
        parts.append(
            f'<clipPath id="row{index}"><rect x="{pad}" y="{row_y:.1f}" height="{cell_h}" width="0">'
            f'<animate attributeName="width" from="0" to="{art_w:.1f}" begin="{delay:.3f}s" '
            f'dur="{row_dur:.3f}s" fill="freeze"/></rect></clipPath>'
        )
        parts.append(f'<g clip-path="url(#row{index})">{text}</g>')
        parts.append(
            f'<rect x="{pad}" y="{row_y + 2:.1f}" width="7" height="{cell_h - 4}" fill="{INK}" opacity="0">'
            f'<animate attributeName="x" from="{pad}" to="{pad + art_w:.1f}" begin="{delay:.3f}s" '
            f'dur="{row_dur:.3f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.9" begin="{delay:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{delay + row_dur:.3f}s"/>'
            f"</rect>"
        )
    status_y = title_h + art_h + 28
    parts.append(
        f'<line x1="0" y1="{title_h + art_h + 8}" x2="{width:.0f}" y2="{title_h + art_h + 8}" stroke="{FRAME}"/>'
    )
    parts.append(
        f'<text x="{width / 2:.0f}" y="{status_y}" fill="{INK}" font-size="14" text-anchor="middle">'
        "Mustafa Avais Kamal</text>"
    )
    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else PREPPED
    lines = rows_from_image(source) if source.exists() else monogram_rows()
    svg = render(lines, static=bool(os.environ.get("STATIC")))
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT} from {source if source.exists() else 'monogram'}")


if __name__ == "__main__":
    main()
