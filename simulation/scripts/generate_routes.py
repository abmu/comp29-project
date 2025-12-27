import os
import random
import argparse
from pathlib import Path
from settings import DIR_PREFIX, NET_NAME, DURATION
from utils import run_command

# Find default SUMO tools
SUMO_HOME = os.environ.get('SUMO_HOME')
if not SUMO_HOME:
    raise EnvironmentError('SUMO_HOME is not set.')

TOOLS = os.path.join(SUMO_HOME, 'tools')
if not os.path.exists(TOOLS):
    raise FileNotFoundError('SUMO tools not found.')

random_trip = os.path.join(TOOLS, 'randomTrips.py')

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--seed', type=int, default=1)
parser.add_argument('--car-density', type=float, default=1.0)
parser.add_argument('--bicycle-density', type=float, default=1.0)
parser.add_argument('--pedestrian-density', type=float, default=1.0)
parser.add_argument('--random-factor', type=float, default=1.0)
parser.add_argument('--foldername', type=str, default='.')
args = parser.parse_args()

random.seed(args.seed)

# Create directory in routes folder
Path(f'{DIR_PREFIX}routes/{NET_NAME}/{args.foldername}/{args.seed}/').mkdir(parents=True, exist_ok=True)

# Configure commands for generating the routes
NETWORK = f'{DIR_PREFIX}networks/{NET_NAME}/main.net.xml'

vehicles = [
    {
        'name': 'car',
        'args': [
            '-n', NETWORK,
            '-e', str(DURATION),
            # '-p', str(10 / args.car_density),
            '--insertion-density', str(1.0 * 100 * args.car_density),
            '--binomial', '100',
            '-o', f'{DIR_PREFIX}routes/{NET_NAME}/{args.foldername}/{args.seed}/car.trips.xml',
            '-r', f'{DIR_PREFIX}routes/{NET_NAME}/{args.foldername}/{args.seed}/car.rou.xml',
            '--fringe-factor', 'max', # ensure the vehicles only spawn from the very edges, rather than the middle of the road
            '--random-factor', f'{random.uniform(1.0, args.random_factor)}', # randomise weight of edges
            '--prefix', 'car',
            '--seed', str(args.seed)
        ]
    },
    {
        'name': 'bicycle',
        'args': [
            '-n', NETWORK,
            '-e', str(DURATION),
            '--insertion-density', str(1.0 * 100 * args.bicycle_density),
            '--binomial', '100',
            '-o', f'{DIR_PREFIX}routes/{NET_NAME}/{args.foldername}/{args.seed}/bicycle.trips.xml',
            '-r', f'{DIR_PREFIX}routes/{NET_NAME}/{args.foldername}/{args.seed}/bicycle.rou.xml',
            '--fringe-factor', 'max',
            '--random-factor', f'{random.uniform(1.0, args.random_factor)}',
            '--prefix', 'bicycle',
            '--vehicle-class', 'bicycle',
            '--seed', str(args.seed)
        ]
    },
    {
        'name': 'pedestrian',
        'args': [
            '-n', NETWORK,
            '-e', str(DURATION),
            '--insertion-density', str(2.0 * 100 * args.pedestrian_density),
            '--binomial', '100',
            '-o', f'{DIR_PREFIX}routes/{NET_NAME}/{args.foldername}/{args.seed}/pedestrian.trips.xml',
            '-r', f'{DIR_PREFIX}routes/{NET_NAME}/{args.foldername}/{args.seed}/pedestrian.rou.xml',
            # '--fringe-factor', 'max',
            '--random-factor', f'{random.uniform(1.0, args.random_factor)}',
            '--prefix', 'pedestrian',
            '--pedestrians',
            '--seed', str(args.seed)
        ]
    }
]


if __name__ == "__main__":
    # generate trips and routes
    # NB: a trip defines a random start A and end B, whereas a route defines the exact edges to traverse to get from that start A to end B
    for v in vehicles:
        print(f'Generating {v["name"]} trips')
        run_command(['python', random_trip] + v['args'])