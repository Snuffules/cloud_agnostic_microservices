#!/usr/bin/env python3
"""
Update the newTag value for one service in one cloud-specific Kustomize overlay.

Example:
  python scripts/update-image-tag.py \
    --service checkout \
    --cloud gcp \
    --new-tag abc123
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


def update_image_tag(path: Path, image_name: str, new_tag: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

    in_images = False
    in_target_image = False
    updated = False
    output: list[str] = []

    for line in lines:
        stripped = line.strip()

        if stripped == "images:":
            in_images = True
            in_target_image = False
            output.append(line)
            continue

        if in_images and stripped.startswith("- name:"):
            current_name = stripped.split(":", 1)[1].strip().strip('"').strip("'")
            in_target_image = current_name == image_name
            output.append(line)
            continue

        if in_images and in_target_image and stripped.startswith("newTag:"):
            indent = line[: len(line) - len(line.lstrip())]
            output.append(f"{indent}newTag: {new_tag}\n")
            updated = True
            in_target_image = False
            continue

        output.append(line)

    if not updated:
        raise ValueError(
            f"Could not find image block with name '{image_name}' and a newTag field in {path}"
        )

    path.write_text("".join(output), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", required=True)
    parser.add_argument("--cloud", required=True, choices=["gcp", "aws", "azure"])
    parser.add_argument("--new-tag", required=True)
    args = parser.parse_args()

    kustomization = Path(
        f"k8s/services/{args.service}/overlays/{args.cloud}/kustomization.yaml"
    )

    image_name = f"{args.service}-image"

    try:
        update_image_tag(kustomization, image_name, args.new_tag)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Updated {kustomization}: {image_name} -> newTag {args.new_tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
