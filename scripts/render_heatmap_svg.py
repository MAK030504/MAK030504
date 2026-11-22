#!/usr/bin/env python3
"""Draw the contribution calendar as an SVG that reveals once, then holds."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
BG = "#0d1117"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
CELL = 11
GAP = 3
STEP = CELL + GAP
LEFT = 36
TOP = 58
PAD = 18


def _columns(days: list[dict]) -> list[list[dict | None]]:
    if not days:
        return []
    by_date = {item["date"]: item for item in days}
    first = date.fromisoformat(days[0]["date"])
    last = date.fromisoformat(days[-1]["date"])
    # weekday(): Monday=0 ... Sunday=6. GitHub's grid starts on Sunday.
    start = first - timedelta(days=(first.weekday() + 1) % 7)
    columns: list[list[dict | None]] = []
    cursor = start
    while cursor <= last:
        column: list[dict | None] = []
        for _ in range(7):
            column.append(by_date.get(cursor.isoformat()))
            cursor += timedelta(days=1)
        columns.append(column)
    return columns


def _month_labels(columns: list[list[dict | None]]) -> list[tuple[int, str]]:
    labels: list[tuple[int, str]] = []
    previous = ""
    last_index = -4
    for index, column in enumerate(columns):
        first = next((cell for cell in column if cell), None)
        if not first:
            continue
        stamp = date.fromisoformat(first["date"]).strftime("%b")
        if stamp != previous and index - last_index >= 3:
            labels.append((index, stamp))
            last_index = index
            previous = stamp
        elif stamp != previous:
            previous = stamp
    return labels


def render(payload: dict) -> str:
    columns = _columns(payload["days"])
    width = LEFT + len(columns) * STEP + PAD
    height = TOP + 7 * STEP + 46
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        f'<rect width="{width}" height="{height}" rx="12" fill="{BG}"/>',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<circle cx="22" cy="16" r="5" fill="#ff5f56"/>',
        f'<circle cx="38" cy="16" r="5" fill="#ffbd2e"/>',
        f'<circle cx="54" cy="16" r="5" fill="#27c93f"/>',
        f'<text x="{width / 2}" y="20" fill="{MUTED}" font-size="12" text-anchor="middle">'
        f'mak@github ~ $ ./contributions.sh</text>',
        f'<line x1="0" y1="32" x2="{width}" y2="32" stroke="{FRAME}"/>',
    ]
    for index, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = TOP + index * STEP + CELL - 1
        parts.append(f'<text x="8" y="{y}" fill="{MUTED}" font-size="10">{name}</text>')
    for index, name in _month_labels(columns):
        x = LEFT + index * STEP
        parts.append(f'<text x="{x}" y="48" fill="{MUTED}" font-size="11">{name}</text>')

    for x, column in enumerate(columns):
        for y, cell in enumerate(column):
            if cell is None:
                continue
            color = PALETTE[min(cell["level"], len(PALETTE) - 1)]
            delay = (x * 7 + y) * 0.004
            px = LEFT + x * STEP
            py = TOP + y * STEP
            parts.append(
                f'<rect x="{px}" y="{py}" width="{CELL}" height="{CELL}" rx="2" fill="{color}">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur="0.35s" fill="freeze"/>'
                f'<animate attributeName="y" from="{py - 6}" to="{py}" begin="{delay:.3f}s" dur="0.35s" fill="freeze"/>'
                f"</rect>"
            )

    total = payload["total"]
    noun = "contribution" if total == 1 else "contributions"
    longest = payload["longest_streak"]
    current = payload["current_streak"]
    footer_y = TOP + 7 * STEP + 22
    parts.append(
        f'<text x="{LEFT}" y="{footer_y}" fill="{INK}" font-size="13">'
        f"{total:,} {noun} in the last year"
        f'<tspan fill="{MUTED}">   ·   current streak {current}d   ·   longest {longest}d</tspan>'
        f"</text>"
    )
    legend_x = width - PAD - 5 * (CELL + 4) - 78
    parts.append(f'<text x="{legend_x}" y="{footer_y}" fill="{MUTED}" font-size="11">Less</text>')
    for level, color in enumerate(PALETTE):
        lx = legend_x + 36 + level * (CELL + 4)
        parts.append(
            f'<rect x="{lx}" y="{footer_y - 10}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>'
        )
    parts.append(
        f'<text x="{legend_x + 36 + 5 * (CELL + 4) + 4}" y="{footer_y}" fill="{MUTED}" font-size="11">More</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    svg = render(payload)
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
