import subprocess


def _generate_routes(seed: int = 42, car_density: float = 1.0, bicycle_density: float = 1.0, pedestrian_density: float = 1.0, random_factor: float = 1.0) -> None:
    # generate a new set of routes in the SUMO simulation
    print(f'Generating new routes... (seed: {seed}, car_density: {car_density}, bicycle_density: {bicycle_density}, pedestrian_density: {pedestrian_density}, random_factor: {random_factor})')
    dir_name = '../simulation/scripts'
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


def set_route(number: int) -> None:
    # set current route for the SUMO simulation
    print(f'Setting route to {number}...')
    dir_name = '../simulation/routes/demo'
    file_names = ['bicycle.rou.xml', 'car.rou.xml', 'pedestrian.rou.xml']
    for f in file_names:
        subprocess.run(
            [
                'cp', f'{number}/{f}', '.'
            ],
            check=True,
            cwd=dir_name
        )


if __name__ == "__main__":
    ROUTES = 1000
    for i in range(1, ROUTES+1):
        _generate_routes(seed=i)