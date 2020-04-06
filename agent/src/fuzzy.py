""" fuzzy matching """

from typing import Optional, List, Set
import numpy as np

LEVENSHTIEN_TRESTHOLD = 2.0


def fuzzy_in(src: Optional[str], targets: Set[str]) -> bool:
    if src is None:
        return False
    res = [fuzzy(src, target) for target in targets]
    return any(res)


def fuzzy(src: str, target: str) -> Optional[str]:
    if levenshtien(src, target) <= LEVENSHTIEN_TRESTHOLD:
        return target
    return None


def levenshtien(src: str, target: str) -> float:
    xsz = len(src) + 1
    ysz = len(target) + 1

    m = np.zeros((xsz, ysz))
    for x in range(xsz):
        m[x, 0] = x
    for y in range(ysz):
        m[0, y] = y

    for x in range(1, xsz):
        for y in range(1, ysz):
            if src[x - 1] == target[y - 1]:
                m[x, y] = min(
                    m[x - 1, y],
                    m[x - 1, y - 1],
                    m[x, y - 1] + 1)
            else:
                m[x, y] = min(
                    m[x - 1, y] + 1,
                    m[x - 1, y - 1] + 1,

                    m[x, y - 1] + 1)
    return m[xsz - 1, ysz - 1]

