import itertools
from functools import cmp_to_key, cache
from typing import Sequence

import pytest

from main import fjmi_sort

count: int

@cache  # FJMI is used when comparisons are most expensive
def comparator(x: int, y: int) -> int:
    global count
    count += 1

    # toy example
    result = -1 if x < y else 0 if x == y else 1
    return result

def stats(seq: Sequence) -> {}:
    global count

    worst = 0
    total = 0
    for perm in itertools.permutations(seq):
        comparator.cache_clear()
        count = 0

        fjmi_sorted = fjmi_sort(perm, comparator)
        worst = max(count, worst)
        total += count
        # noinspection PyTypeChecker
        assert fjmi_sorted == (py_sorted := sorted(perm, key=cmp_to_key(comparator))), (fjmi_sorted, py_sorted)
    return {'worst': worst, 'total': total}


def test_permutations_of_01234() -> None:
    # https://stackoverflow.com/q/1935194/1935353#comment57146754_1935491
    assert (x := stats([0, 1, 2, 3, 4])) == {'worst': 7, 'total': 832}, x

def test_permutations_of_5231476() -> None:
    # https://github.com/decidedlyso/merge-insertion-sort#user-content-the-algorithm
    assert (x := stats([5, 2, 3, 1, 4, 7, 6])) == {'worst': 13, 'total': 62784}, x

# https://github.com/decidedlyso/merge-insertion-sort#user-content-performance
def test_permutations_of_ranges_1_to_8() -> None:
    for len_ in range(1, 9):
        assert stats(range(len_))['worst'] == [0, 1, 3, 5, 7, 10, 13, 16][len_ - 1]

# @pytest.mark.skip
def test_permutations_of_range_9_slow() -> None:
    assert stats(range(9))['worst'] == 19

@pytest.mark.skip
def test_permutations_of_range_10_very_slow() -> None:
    assert stats(range(10))['worst'] == 22
