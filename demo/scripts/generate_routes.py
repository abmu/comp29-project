import os
import shutil
from pathlib import Path
from utils import run_command

NET_NAME = 'demo'
DIR_PREFIX = '../'
NETWORK = f'{DIR_PREFIX}networks/{NET_NAME}.net.xml'
DURATION = '1000' # Seconds - for how long new entities should be spawned
SEED = '42'

# Find default SUMO tools
SUMO_HOME = os.environ.get('SUMO_HOME')
TOOLS = os.path.join(SUMO_HOME, 'tools')

if not SUMO_HOME or not os.path.exists(TOOLS):
    raise EnvironmentError('SUMO_HOME is not set, or SUMO tools not found.')

# Create directory in routes folder
Path(f'{DIR_PREFIX}routes/{NET_NAME}/').mkdir(exist_ok=True)




# POISSSON

# RANDOM DEPART

# ADD EXTRA PEDESTRIAN WALK PATH GOING INTO/FROM SCHOOL BUILDING AND PARKS





vehicles = [
    {
        'name': 'car',
        'args': [
            '-n', NETWORK,
            '-e', DURATION,
            '-p', '5',
            '-o', f'{DIR_PREFIX}routes/{NET_NAME}/car.trips.xml',
            '-r', f'{DIR_PREFIX}routes/{NET_NAME}/car.rou.xml',
            '--fringe-factor', 'max', # ensure the vehicles only spawn from the very edges, rather than the middle of the road
            '--prefix', 'car',
            '--seed', SEED
        ]
    },
    {
        'name': 'bicycle',
        'args': [
            '-n', NETWORK,
            '-e', DURATION,
            '-p', '10',
            '-o', f'{DIR_PREFIX}routes/{NET_NAME}/bicycle.trips.xml',
            '-r', f'{DIR_PREFIX}routes/{NET_NAME}/bicycle.rou.xml',
            '--fringe-factor', 'max',
            '--prefix', 'bicycle',
            '--vehicle-class', 'bicycle',
            '--seed', SEED
        ]
    },
    {
        'name': 'pedestrian',
        'args': [
            '-n', NETWORK,
            '-e', DURATION,
            '-p', '3',
            '-o', f'{DIR_PREFIX}routes/{NET_NAME}/pedestrian.trips.xml',
            '-r', f'{DIR_PREFIX}routes/{NET_NAME}/pedestrian.rou.xml',
            '--fringe-factor', 'max',
            '--prefix', 'pedestrian',
            '--pedestrians',
            '--seed', SEED
        ]
    }
]

for v in vehicles:
    print(f'Generating {v["name"]} trips')
    random_trip = os.path.join(TOOLS, 'randomTrips.py')
    duarouter = shutil.which('duarouter')

    # generate trip and route
    # NB: a trip defines a random start A and end B, whereas a route defines the exact edges to traverse to get from that start A to end B
    run_command(['python', random_trip] + v['args'])