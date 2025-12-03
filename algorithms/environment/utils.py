def ceil(x: float) -> int:
    # return the ceil of a number
    return int(x) + (x % 1 > 0)


def file_dump(file_name: str, *args: str) -> None:
    # dump content straight into file
    with open(file_name, 'w') as f:
        f.write('\n'.join(args))


def file_eval(file_name: str) -> list[any]:
    # evaluate the lines of the file
    content = []
    with open(file_name, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            content.append(eval(line))
    return content
