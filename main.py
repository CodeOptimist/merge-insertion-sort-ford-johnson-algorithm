# Ford–Johnson merge-insertion algorithm for minimal comparisons implemented in Python.
#
# Thanks to:
# https://github.com/decidedlyso/merge-insertion-sort
# https://en.wikipedia.org/wiki/Merge-insertion_sort
# https://codereview.stackexchange.com/questions/116367/ford-johnson-merge-insertion-sort
# https://stackoverflow.com/questions/1935194/sorting-an-array-with-minimal-number-of-comparisons

# Shoutout to:
# https://github.com/PunkChameleon/ford-johnson-merge-insertion-sort
# https://github.com/tomdalling/ford_johnson

import bisect
from functools import cmp_to_key
from typing import Sequence, Callable, Any, List

Comparator = Callable[[Any, Any], int]


def fjmi_sort(seq: Sequence, comp: Comparator) -> List:
    if len(seq) < 2:
        return list(seq)  # longer sequences will be a list; let's be consistent

    pairs = zip(seq[::2], seq[1::2])
    # https://en.wikipedia.org/wiki/Merge-insertion_sort#Algorithm
    # `reverse=True` "smaller indexes to larger indexes [...] but within each group [...] larger indexes to smaller indexes"
    sorted_pairs = list(sorted(pair, key=cmp_to_key(comp), reverse=True) for pair in pairs)
    sorted_pairs = fjmi_sort(sorted_pairs, lambda x, y: comp(x[0], y[0]))  # Recursion using first elements.

    main_chain, pending_elements = map(list, zip(*sorted_pairs))  # unzip lists
    if len(seq) % 2 == 1:
        pending_elements.append(seq[-1])

    a_positions = list(range(len(main_chain)))

    def pending_element_indexes(len_: Any) -> Sequence:
        def jacobsthal_number(idx: int) -> int:
            return round((2 ** idx + (-1) ** (idx - 1)) / 3)

        # https://en.wikipedia.org/wiki/Jacobsthal_number
        # 0 1 1 3 5 11 21 43 85 171 341 683 ...
        seq = []
        for i in range(len_):
            num = jacobsthal_number(i)
            if num >= len_:
                break
            seq.append(num)

        seq.append(len_)

        # https://github.com/decidedlyso/merge-insertion-sort#user-content-the-algorithm
        # 1   3 2   5 4   11 10 9 8 7 6   21 20 19 18 ...
        # (but 0-indexed)
        result = []
        for i in range(1, len(seq)):
            result += [x - 1 for x in range(seq[i], seq[i - 1], -1)]

        return result

    for b_index in pending_element_indexes(len(pending_elements)):
        def binary_insert() -> None:
            nonlocal a_positions
            val = pending_elements[b_index]
            # https://github.com/decidedlyso/merge-insertion-sort#user-content-the-algorithm
            if b_index < len(a_positions):
                # this is the main benefit of FJMI...I think? #todo
                search_chain = main_chain[:a_positions[b_index]]
            else:
                search_chain = main_chain

            key_func = cmp_to_key(comp)
            # noinspection PyArgumentList
            # `key_func(val)` not `val` https://github.com/python/cpython/issues/91966
            insertion_idx = bisect.bisect_left(search_chain, key_func(val), key=key_func)

            for idx, a_position in enumerate(a_positions):
                if a_position >= insertion_idx:
                    a_positions[idx] += 1

            main_chain.insert(insertion_idx, val)

        # fewer comparisons than
        #  bisect.insort_left(main_chain, pending_elements[b_index], key=cmp_to_key(comp))
        # because of our partial `search_chain`
        binary_insert()
    return main_chain
