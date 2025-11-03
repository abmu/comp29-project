import subprocess


def run_command(cmd: list[str]) -> None:
    '''Run command and stream its output'''
    print(f'Running > {" ".join(cmd)}')
    res = subprocess.run(cmd, text=True)
    if res.returncode != 0:
        raise RuntimeError(f'Command failed: {" ".join(cmd)}')
