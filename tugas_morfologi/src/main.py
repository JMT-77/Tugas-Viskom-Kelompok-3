# """Command-line entry point for the morphology assignment."""
# from __future__ import annotations

# import argparse
# from pathlib import Path

# from operations import process_to_montage


# def main() -> None:
#     parser = argparse.ArgumentParser(
#         description=(
#             "Run dilation, erosion, opening, closing, top-hat, hit-or-miss, "
#             "skeletonization, and thinning, then save one composite PNG."
#         )
#     )
#     parser.add_argument("input", help="input PNG, preferably a dark-ink document scan")
#     parser.add_argument("output", help="one PNG containing all operation results")
#     parser.add_argument(
#         "--kernel",
#         type=int,
#         choices=(3, 5, 7),
#         default=3,
#         help="odd cross-shaped structuring-element size (default: 3)",
#     )
#     args = parser.parse_args()
#     report = process_to_montage(args.input, args.output, kernel_size=args.kernel)
#     results = report["results"]
#     print(f"Processed {len(results) - 2} morphology operations")
#     print(f"Saved composite PNG: {Path(args.output)}")
#     print(f"Input size: {report['input'].shape[1]}x{report['input'].shape[0]}")


# if __name__ == "__main__":
#     main()

"""Jalankan 8 operasi morfologi pada 8 citra: satu PNG komposit + satu PNG per operasi."""
from __future__ import annotations

import argparse
from pathlib import Path
from dataclasses import dataclass, replace

from operations import process_to_montage, save_per_operation


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input_dir", help="folder berisi dilasi.png, erosi.png, dst.")
    p.add_argument("output", help="file PNG komposit hasil")
    p.add_argument("--per-op-dir", default=None,
                   help="folder PNG per operasi (default: <folder output>/per_operasi)")
    a = p.parse_args()
    results = process_to_montage(a.input_dir, a.output)
    per_op_dir = Path(a.per_op_dir) if a.per_op_dir else Path(a.output).parent / "per_operasi"
    paths = save_per_operation(results, per_op_dir)
    for r in results:
        print(f"{r['name']:<16} {r['note']}")
    print(f"Komposit : {a.output}")
    print(f"Per operasi ({len(paths)} file): {per_op_dir}")


if __name__ == "__main__":
    main()