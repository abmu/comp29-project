def ceil(x: float) -> int:
    # return the ceil of a number
    return int(x) + (x % 1 > 0)