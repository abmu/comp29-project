import subprocess

ROUTES = 1000


def _generate_routes(seed: int = 1, car_density: float = 1.0, bicycle_density: float = 1.0, pedestrian_density: float = 1.0, random_factor: float = 1.0) -> None:
    # generate a new set of routes in the SUMO simulation
    print(f'Generating new routes... (seed: {seed}, car_density: {car_density}, bicycle_density: {bicycle_density}, pedestrian_density: {pedestrian_density}, random_factor: {random_factor})')
    dir_name = '.'
    script_name = 'generate_routes.py'
    subprocess.run(
        [
            'python', script_name,
            '--seed', str(seed),
            '--car-density', str(car_density),
            '--bicycle-density', str(bicycle_density),
            '--pedestrian-density', str(pedestrian_density),
            '--random-factor', str(random_factor),
        ],
        stdout=subprocess.DEVNULL,
        check=True,
        cwd=dir_name
    )


if __name__ == "__main__":
    for i in range(1, ROUTES+1):
        _generate_routes(seed=i)