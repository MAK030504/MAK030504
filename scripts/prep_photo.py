#!/usr/bin/env python3
"""Turn a portrait photo into the grayscale image make_ascii_svg.py expects.

Usage:
    python scripts/prep_photo.py source-photo.jpg

The default profile mark is the MAK monogram, because the GitHub avatar is
an identicon. Run this only when you want that mark replaced by a photo.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "source-prepped.png"


def prep(source: Path) -> None:
    image = Image.open(source).convert("RGB")
    image = ImageOps.exif_transpose(image)
    image = ImageOps.fit(image, (640, 800), method=Image.Resampling.LANCZOS, centering=(0.5, 0.35))
    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray, cutoff=1)
    gray = ImageEnhance.Contrast(gray).enhance(1.35)
    # Lift the background toward white so it becomes spaces in the ASCII ramp.
    pixels = gray.load()
    for y in range(gray.height):
        for x in range(gray.width):
            value = pixels[x, y]
            if value > 210:
                pixels[x, y] = 255
    gray.save(OUT)
    print(f"wrote {OUT}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python scripts/prep_photo.py source-photo.jpg")
    prep(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
