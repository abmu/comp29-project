def ceil(x: float) -> int:
    # return the ceil of a number
    return int(x) + (x % 1 > 0)


def file_dump(file_name: str, *args: str) -> None:
    # dump content straight into file
    with open(file_name, 'w') as f:
        f.write('\n'.join(args))
