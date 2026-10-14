"""Command-line entry point for the morphology assignment."""
from __future__ import annotations

import argparse
from pathlib import Path

from operations import process_to_montage


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run dilation, erosion, opening, closing, top-hat, hit-or-miss, "
            "skeletonization, and thinning, then save one composite PNG."
        )
    )
    parser.add_argument("input", help="input PNG, preferably a dark-ink document scan")
    parser.add_argument("output", help="one PNG containing all operation results")
    parser.add_argument(
        "--kernel",
        type=int,
        choices=(3, 5, 7),
        default=3,
        help="odd cross-shaped structuring-element size (default: 3)",
    )
    args = parser.parse_args()
    report = process_to_montage(args.input, args.output, kernel_size=args.kernel)
    results = report["results"]
    print(f"Processed {len(results) - 2} morphology operations")
    print(f"Saved composite PNG: {Path(args.output)}")
    print(f"Input size: {report['input'].shape[1]}x{report['input'].shape[0]}")


if __name__ == "__main__":
    main()
