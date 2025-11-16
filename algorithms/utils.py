import subprocess


def ceil(x: float) -> int:
    # return the ceil of a number
    return int(x) + (x % 1 > 0)


def generate_routes(seed: int = 42, car_density: float = 1.0, bicycle_density: float = 1.0, pedestrian_density: float = 1.0) -> None:
    # generate a new set of routes in the SUMO simulation
    print('Generating new routes...')
    dir_name = '../simulation/scripts'
    script_name = 'generate_routes.py'
    subprocess.run(
        [
            'python', script_name,
            '--seed', str(seed),
            '--car-density', str(car_density),
            '--bicycle-density', str(bicycle_density),
            '--pedestrian-density', str(pedestrian_density),
        ],
        stdout=subprocess.DEVNULL,
        check=True,
        cwd=dir_name
    )


def file_dump(file_name: str, *args: str) -> None:
    # dump content straight into file
    with open(file_name, 'w') as f:
        f.write('\n'.join(args))
