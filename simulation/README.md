# Simulation

This folder contains the SUMO (Simulation of Urban MObility) network definitions, routes, and scripts for generating diverse traffic scenarios. It provides the simulation environment used for training and evaluating traffic light control algorithms.

## Overview

The simulation environment models urban traffic networks with:
- **Three distinct network topologies**: Demo, Crossing, and Extended
- **Semi-realistic traffic**: Cars, bicycles, and pedestrians with randomised routes -- with adjustable traffic density
- **Sensor simulation**: Lane area detectors and induction loops for vehicle/pedestrian detection

## Structure

```
simulation/
├── README.md                    # This file
├── simulation.sumocfg           # Main SUMO configuration file
├── statistics.xml               # Statistics collection
├── viewsettings.xml             # GUI view settings
├── networks/                    # Network definitions
│   ├── demo/                    
│   │   ├── main.net.xml         # Network topology
│   │   ├── detectors.add.xml    # Detector definitions
│   │   └── detector.*.xml       # Individual detector data
│   ├── crossing/                
│   │   ├── main.net.xml         # Zebra crossing
│   │   ├── tls.net.xml          # Replaced with TLS
│   │   └── detectors.add.xml
│   └── extended/                
│       ├── main.net.xml
│       └── detectors.add.xml
├── routes/                      # Traffic routes
│   ├── demo/
│   │   ├── bicycle.rou.xml      # Current bicycle routes
│   │   ├── car.rou.xml          # Current car routes
│   │   ├── pedestrian.rou.xml   # Current pedestrian routes
│   │   ├── train/               # Training scenarios
│   │   │   └── {seed}/          # Unique seed folders
│   │   │       ├── car.rou.xml
│   │   │       ├── bicycle.rou.xml
│   │   │       └── pedestrian.rou.xml
│   │   └── eval/                # Evaluation scenarios
│   │       └── {seed}/
│   ├── crossing/
│   └── extended/
├── scripts/                     # Route generation scripts
│   ├── batch.py                 # Batch route generation
│   ├── generate_routes.py       # Individual route generation
│   └── utils.py                 # Utility functions
└── images/                      # OpenStreetMap background image
```

## Notation Guide

The traffic light system (TLS) ID is equivalent to the Connecting Junction (CJ) which it controls, e.g. CJ_1.

Lanes names:
- (Street Name)\_(Lane Number)\_(Segment Number)

Junction names: 
- EJ\_(X) -> Edge/End Junction X
- CJ\_(Y) -> Connecting Junction Y

Detector names:
- CJ\_(X)\_(N/E/S/W)B_(Y)_(Z) -> Connecting Junction X, N/E/S/W Bound, Side Y, Lane Z

## Networks

Three networks were created, with different TLS available:
1. `demo` (CJ_1)
2. `crossing` (CJ_2)
3. `extended` (CJ_1, CJ_2, CJ_9)

To view and interact with the simulation visually, edit `simulation.sumocfg` with the:
- Network file to load
- Route files to use
- Additional detectors and sensors

And then run the simulation:
```bash
sumo-gui simulation.sumocfg
```

This opens the GUI with the network, routes, and detectors loaded. You can:
- Play/pause the simulation
- Speed up/slow down

To modify network topology using `netedit`, do for example:

```bash
netedit networks/demo/main.net.xml  # Open the demo network in netedit editor
```

Useful keyboard shortcuts in `netedit`:
- **F10**: Open edit options menu
  - Enable "Lefthand traffic" for left-hand driving
- **F9**: Open visualisation options
  - Go to "Junctions" and click "Show link tls index" to display traffic light phase numbers

### Network files (.net.xml)
Define the physical network topology:
- Junctions and connections
- Lanes and priorities
- Default traffic light logic
- Pedestrian crossings

## Routes

Generate a single route set for the three entities (car, bicycle, pedestrian):
```bash
cd scripts
python generate_routes.py --netname demo --seed 1 --foldername train
```

**Options**:
- `--netname`: Network name (demo, crossing, extended)
- `--seed`: Random seed for reproducibility
- `--car-density`: Vehicle density multiplier (default: 1.0)
- `--bicycle-density`: Bicycle density multiplier (default: 1.0)
- `--pedestrian-density`: Pedestrian density multiplier (default: 1.0)
- `--random-factor`: Route randomisation factor (default: 1.0)
- `--foldername`: Destination folder (train, eval, or custom)

Generate routes in batch:
```bash
cd scripts
python batch.py
```
By default, this generates:
- 1000 training routes per network with standard density
- 100 evaluation routes per network with various density combinations

### Route files (.rou.xml)
The generation scripts call the `randomTrips.py` provided by SUMO to produce two types of files:
- **Trips** (.rou.xml): Origin-destination pairs
- **Routes** (.trips.xml): Specific sequences of edges to traverse (though this type is not used)

## Usage with `algorithms/`

There are two detectors used for the road users (cars + bicycles), which the agents receive state from:

- **Lane Area Detectors**:
  - Placed on lanes approaching a junction
  - Measures vehicle waiting times

- **Induction Loops**:
  - Placed on lanes exiting a junction
  - Measures vehicle throughput

This simulation environment is integrated with the algorithms folder:

1. **Path configuration** in `algorithms/run.py`:
   ```python
   DIR_PREFIX = '../simulation/'
   ```

2. **Network loading**:
   ```python
   from environment import get_sumo_cfg
   sumo_cfg = get_sumo_cfg(DIR_PREFIX, NET_NAME)
   ```

3. **Route selection**:
   - Training mode uses `routes/{NET_NAME}/train/`
   - Evaluation mode uses `routes/{NET_NAME}/eval/`

Where `NET_NAME` is one of the three network names.

## Dependencies

### Required Software
- **SUMO** (Simulation of Urban MObility)
  -- Includes `sumo-gui`, `netedit`, and Python tools (`randomTrips.py`, etc.)
- **Python 3.8+** (standard library only)

### Installation

1. **Install SUMO**:
   ```bash
   sudo apt-get install sumo sumo-tools sumo-doc
   ```

2. **Set SUMO_HOME environment variable**:
   ```bash
   # Add environment variable e.g. to ~/.bashrc or ~/.zshrc
   export SUMO_HOME="/usr/share/sumo"
   ```

3. **Verify installation**:
   ```bash
   sumo --version
   sumo-gui --help
   ```