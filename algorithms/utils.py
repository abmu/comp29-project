from pathlib import Path


def file_dump(file_name: str, *args: str) -> None:
    # ensure parent directory exists
    path = Path(file_name)
    path.parent.mkdir(parents=True, exist_ok=True)

    # dump content straight into file
    with open(path, 'w') as f:
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
