# from __future__ import annotations

# import sys
# from pathlib import Path

# import cv2
# import numpy as np

# sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# from operations import (  # noqa: E402
#     binarize_document,
#     dilation,
#     erosion,
#     hit_or_miss,
#     morphology_kernel,
#     opening,
#     run_all,
#     skeletonization,
#     thinning,
# )


# def test_all_operations_return_same_shape() -> None:
#     gray = np.full((80, 120), 255, dtype=np.uint8)
#     cv2.rectangle(gray, (20, 20), (90, 55), 0, 3)
#     results = run_all(gray)
#     assert len(results) == 10
#     assert all(image.shape == gray.shape for image in results.values())
#     assert all(image.dtype == np.uint8 for image in results.values())


# def test_basic_binary_operations_change_a_small_shape() -> None:
#     binary = np.zeros((15, 15), dtype=np.uint8)
#     binary[6:9, 6:9] = 255
#     kernel = morphology_kernel(3)
#     assert cv2.countNonZero(dilation(binary, kernel)) > cv2.countNonZero(binary)
#     assert cv2.countNonZero(erosion(binary, kernel)) < cv2.countNonZero(binary)
#     assert opening(binary, kernel).shape == binary.shape


# def test_skeleton_and_thinning_are_binary() -> None:
#     binary = np.zeros((30, 30), dtype=np.uint8)
#     binary[5:25, 13:17] = 255
#     binary[13:17, 5:25] = 255
#     skeleton = skeletonization(binary, morphology_kernel())
#     thin = thinning(binary)
#     assert set(np.unique(skeleton)).issubset({0, 255})
#     assert set(np.unique(thin)).issubset({0, 255})
#     assert cv2.countNonZero(skeleton) > 0
#     assert cv2.countNonZero(thin) > 0


# def test_hit_or_miss_finds_an_endpoint() -> None:
#     line = np.zeros((9, 9), dtype=np.uint8)
#     line[4, 2:7] = 255
#     marks = hit_or_miss(thinning(line))
#     assert cv2.countNonZero(marks) >= 1


# def test_binarize_document_uses_white_foreground() -> None:
#     gray = np.full((5, 5), 255, dtype=np.uint8)
#     gray[2, 2] = 0
#     binary = binarize_document(gray)
#     assert binary[2, 2] == 255
#     assert binary[0, 0] == 0

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from operations import (  # noqa: E402
    CASES, count_components, dilation, erosion, hit_or_miss, make_kernel,
    remove_small, skeletonization, thinning,
)


def test_dilation_grows_and_erosion_shrinks() -> None:
    b = np.zeros((15, 15), np.uint8)
    b[6:9, 6:9] = 255
    k = make_kernel("cross", 3)
    assert cv2.countNonZero(dilation(b, k)) > cv2.countNonZero(b)
    assert cv2.countNonZero(erosion(b, k)) < cv2.countNonZero(b)


def test_hit_or_miss_finds_four_corners_of_a_square() -> None:
    b = np.zeros((20, 20), np.uint8)
    b[5:15, 5:15] = 255
    assert cv2.countNonZero(hit_or_miss(b)) == 4


def test_skeleton_and_thinning_are_binary() -> None:
    b = np.zeros((30, 30), np.uint8)
    b[5:25, 13:17] = 255
    b[13:17, 5:25] = 255
    for out in (skeletonization(b, make_kernel()), thinning(b)):
        assert set(np.unique(out)) <= {0, 255}
        assert cv2.countNonZero(out) > 0


def test_remove_small_drops_tiny_components() -> None:
    b = np.zeros((20, 20), np.uint8)
    b[2, 2] = 255
    b[8:14, 8:14] = 255
    assert count_components(remove_small(b, 5)) == 1


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.name)
def test_input_file_exists(case) -> None:
    path = ROOT / "data" / "input" / case.file
    if not path.exists():
        pytest.skip(f"{case.file} belum ada di data/input/")
    assert cv2.imread(str(path)) is not None