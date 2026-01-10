import subprocess

NET_NAMES = [
    'demo',
    'crossing',
    'extended'
]

ROUTES = 1000
TRAIN_ROUTE = {'car_density': 1.0, 'bicycle_density': 1.0, 'pedestrian_density': 1.0}

EVAL_ROUTES_PER = 10
EVAL_ROUTES = [
    TRAIN_ROUTE,
    {'car_density': 1.5, 'bicycle_density': 1.5, 'pedestrian_density': 1.5},
    {'car_density': 0.5, 'bicycle_density': 0.5, 'pedestrian_density': 0.5},
    {'car_density': 1.5, 'bicycle_density': 1.5, 'pedestrian_density': 0.5},
    {'car_density': 0.5, 'bicycle_density': 0.5, 'pedestrian_density': 1.5},
]


def _generate_routes(netname: str, seed: int = 1, car_density: float = 1.0, bicycle_density: float = 1.0, pedestrian_density: float = 1.0, random_factor: float = 1.0, foldername: str = '.') -> None:
    # generate a new set of routes in the SUMO simulation
    print(f'Generating new routes... (seed: {seed}, car_density: {car_density}, bicycle_density: {bicycle_density}, pedestrian_density: {pedestrian_density}, random_factor: {random_factor})')
    dir_name = '.'
    script_name = 'generate_routes.py'
    subprocess.run(
        [
            'python', script_name,
            '--netname', netname,
            '--seed', str(seed),
            '--car-density', str(car_density),
            '--bicycle-density', str(bicycle_density),
            '--pedestrian-density', str(pedestrian_density),
            '--random-factor', str(random_factor),
            '--foldername', foldername
        ],
        stdout=subprocess.DEVNULL,
        check=True,
        cwd=dir_name
    )


if __name__ == "__main__":
    netnames = ', '.join(NET_NAMES)

    print(f'Generating {ROUTES} "train" routes each for the networks "{netnames}"...')
    for i in range(1, ROUTES+1):
        for netname in NET_NAMES:
            _generate_routes(netname, seed=i, **TRAIN_ROUTE, foldername='train')

    print(f'\nGenerating {EVAL_ROUTES_PER * len(EVAL_ROUTES)} "eval" routes each for the networks "{netnames}"...')
    for i, params in enumerate(EVAL_ROUTES, start=1):
        for j in range(1, EVAL_ROUTES_PER+1):
            seed = EVAL_ROUTES_PER * (i-1) + j
            for netname in NET_NAMES:
                _generate_routes(netname, seed=seed, **params, foldername='eval')