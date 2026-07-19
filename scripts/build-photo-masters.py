#!/usr/bin/env python3
"""Build web-sized progressive JPEG masters for the photography blog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageOps


def build_master(source: Path, destination: Path, max_edge: int, quality: int) -> dict[str, object]:
    with Image.open(source) as original:
        icc_profile = original.info.get("icc_profile")
        image = ImageOps.exif_transpose(original).convert("RGB")
        image.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)

        destination.parent.mkdir(parents=True, exist_ok=True)
        save_options: dict[str, object] = {
            "format": "JPEG",
            "quality": quality,
            "optimize": True,
            "progressive": True,
            "subsampling": 1,
        }
        if icc_profile:
            save_options["icc_profile"] = icc_profile
        image.save(destination, **save_options)

        return {
            "name": source.stem,
            "width": image.width,
            "height": image.height,
            "bytes": destination.stat().st_size,
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="Directory containing source JPEG files")
    parser.add_argument("destination", type=Path, help="Directory for generated masters")
    parser.add_argument("--max-edge", type=int, default=2400)
    parser.add_argument("--quality", type=int, default=88)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()

    photos = []
    for source in sorted(args.source.glob("*.jpeg")):
        destination = args.destination / f"{source.stem}.jpg"
        photos.append(build_master(source, destination, args.max_edge, args.quality))

    manifest = {"photos": photos}
    output = json.dumps(manifest, indent=2)
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
