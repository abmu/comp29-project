# Simulation

This folder contains the SUMO (Simulation of Urban MObility) network definitions, routes, and scripts for generating realistic traffic scenarios. It provides the simulation environment used for training and evaluating traffic light control algorithms.

## Overview

The simulation environment models urban traffic networks with:
- **Three distinct network topologies**: Demo (single junction), Crossing (with pedestrians), and Extended (multi-junction)
- **Realistic traffic**: Cars, bicycles, and pedestrians with randomized routes
- **Sensor simulation**: Lane area detectors and induction loops for vehicle/pedestrian detection
- **Parametric route generation**: Adjustable traffic density for training and evaluation

## Dependencies

### Required Software
- **SUMO** - Simulation of Urban MObility
  - Includes `sumo-gui`, `netedit`, and Python tools (`randomTrips.py`, etc.)

### Python (for route generation)
- Python 3.6+
- No external Python packages required (uses standard library only)

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

## Project Structure

```
simulation/
├── README.md                    # This file
├── simulation.sumocfg           # Main SUMO configuration file
├── statistics.xml              # Statistics collection configuration
├── viewsettings.xml            # GUI view settings
├── networks/                    # Network definitions
│   ├── demo/                   # Single junction network
│   │   ├── main.net.xml       # Network topology
│   │   ├── detectors.add.xml  # Detector definitions
│   │   └── detector.*.xml     # Individual detector configurations
│   ├── crossing/               # Junction with pedestrian crossing
│   │   ├── main.net.xml
│   │   ├── tls.net.xml        # Traffic light systems
│   │   └── detectors.add.xml
│   └── extended/               # Multi-junction network
│       ├── main.net.xml
│       └── detectors.add.xml
├── routes/                      # Traffic routes
│   ├── demo/
│   │   ├── bicycle.rou.xml    # Base bicycle routes
│   │   ├── car.rou.xml        # Base car routes
│   │   ├── pedestrian.rou.xml # Base pedestrian routes
│   │   ├── train/             # Training scenarios
│   │   │   └── {seed}/        # Unique seed folders
│   │   │       ├── car.rou.xml
│   │   │       ├── bicycle.rou.xml
│   │   │       └── pedestrian.rou.xml
│   │   └── eval/              # Evaluation scenarios
│   │       └── {seed}/
│   ├── crossing/
│   └── extended/
├── scripts/                     # Route generation scripts
│   ├── batch.py                # Batch route generation
│   ├── generate_routes.py      # Individual route generation
│   └── utils.py                # Utility functions
└── images/                      # Network visualizations
```

## Quick Start

### 1. Running the Simulation GUI

To view and interact with the simulation visually:

```bash
cd /path/to/simulation
sumo-gui simulation.sumocfg
```

This opens the GUI with the network, routes, and detectors loaded. You can:
- Play/pause the simulation
- Speed up/slow down
- View vehicle trajectories
- Monitor detector activations

### 2. Running Headless Simulation

For computational efficiency without GUI:

```bash
sumo -c simulation.sumocfg
```

### 3. Generating Routes

#### Generate a single route set:
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
- `--random-factor`: Route randomization factor (default: 1.0)
- `--foldername`: Destination folder (train, eval, or custom)

#### Generate routes in batch:
```bash
cd scripts
python batch.py
```

This generates:
- 1000 training routes per network with standard density
- 100 evaluation routes per network with various density combinations

**Evaluation density configurations**:
1. Standard (1.0, 1.0, 1.0)
2. High density (1.5, 1.5, 1.5)
3. Low density (0.5, 0.5, 0.5)
4. High vehicles/bicycles, low pedestrians (1.5, 1.5, 0.5)
5. Low vehicles/bicycles, high pedestrians (0.5, 0.5, 1.5)

## Network Definitions

### Demo Network (CJ_1)
Single urban junction with controlled traffic flow.

**Features**:
- 4 approaches: North, South, East, West
- 2 lanes per approach (vehicles)
- 8-phase traffic light system
- 14 lane area detectors (queue measurement)
- 8 induction loops (throughput measurement)
- Pedestrian crossings on all 4 sides

**Use case**: Single-agent traffic light optimization

### Crossing Network (CJ_2)
Urban junction with prominent pedestrian crossing.

**Features**:
- 4 approaches with varying lane configurations
- Dedicated pedestrian crossing area
- 2 main driving phases + pedestrian phase
- Focus on balancing vehicle and pedestrian flow
- Pedestrian waiting area detectors

**Use case**: Multi-objective optimization (vehicles + pedestrians)

### Extended Network (CJ_1, CJ_2, CJ_9)
Three interconnected junctions requiring coordinated control.

**Features**:
- 3 traffic light systems
- Complex traffic patterns with interconnections
- 40+ detectors across all junctions
- Adjacent junction relationships: 
  - CJ_1 connects to CJ_2 and CJ_9
  - CJ_2 connects to CJ_1
  - CJ_9 connects to CJ_1

**Use case**: Multi-agent coordination and communication

## Detector Architecture

### Detector Types

**Lane Area Detectors** (laneAreaDetector):
- Positioned upstream of junctions
- Measure vehicle waiting times
- 30-50m detection length
- Report max waiting time every 300 seconds

**Induction Loops** (inductionLoop):
- Positioned just before stop line
- Count vehicles crossing per time period
- Measure vehicle throughput
- 300-second reporting interval

### Naming Convention

**Queue Detector** (upstream):
- Format: `CJ_{X}_{DIR}B_1_{Y}`
- Example: `CJ_1_NB_1_1` = Junction 1, North Bound, Lane 1
- Used to detect vehicle queues

**Throughput Detector** (downstream):
- Format: `CJ_{X}_{DIR}B_2_{Y}`
- Example: `CJ_1_NB_2_1` = Junction 1, North Bound, Loop 1
- Used to count vehicles passing

**Direction codes**:
- NB = North Bound
- SB = South Bound
- EB = East Bound
- WB = West Bound

## Route Generation Details

### Route File Format
Routes are generated in SUMO's `.rou.xml` format, consisting of:
- **Trips**: Origin-destination pairs
- **Routes**: Specific sequences of edges/lanes to traverse

### Generation Process

1. **Trip generation** using `randomTrips.py`:
   - Creates random origin-destination pairs
   - Distributed across network edges
   - Respects fringe factor (edges must start/end at network boundary)

2. **Route computation**:
   - SUMO's routing engine computes shortest paths
   - Takes into account road speeds and networks

3. **Randomization**:
   - `--random-factor`: Controls route variation
   - `--binomial`: 100 ensures balanced distribution

### Entity Types

**Cars** (`car.rou.xml`):
- Insertion density: 100 × car_density per hour/km
- Vehicle class: passenger vehicles
- Speed: network-dependent

**Bicycles** (`bicycle.rou.xml`):
- Insertion density: 100 × bicycle_density per hour/km
- Vehicle class: bicycle
- Lower speed than cars
- Can share certain lanes

**Pedestrians** (`pedestrian.rou.xml`):
- Insertion density: 200 × pedestrian_density per hour/km
- Require dedicated pedestrian crossing edges
- Use crossings at junctions

## Configuration Files

### simulation.sumocfg
Main SUMO configuration that specifies:
- Network file to load
- Route files to use
- Additional detectors and sensors
- GUI settings for visualization

**Typical structure**:
```xml
<input>
    <net-file value="networks/demo/main.net.xml"/>
    <route-files value="routes/demo/car.rou.xml,routes/demo/bicycle.rou.xml,routes/demo/pedestrian.rou.xml"/>
    <additional-files value="networks/demo/detectors.add.xml"/>
</input>
```

### detectors.add.xml
Defines all sensors for a network:
- Induction loops (vehicle counting)
- Lane area detectors (queue detection)
- Output file specifications

### Network Files (.net.xml)
Define the physical network topology:
- Junctions and connections
- Lanes and speeds
- Traffic light logic
- Pedestrian facilities

## Usage in Algorithms

The simulation environment is integrated with the algorithms folder:

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

## Advanced Features

### Network Editing with netedit

To modify network topology:

```bash
sumo-gui -e networks/demo/main.net.xml  # Opens netedit editor
```

**Useful keyboard shortcuts in netedit**:
- **F10**: Open edit options menu
  - Enable "Lefthand traffic" for left-hand driving
- **F9**: Open visualization options
  - Go to "Junctions" → "Show link tls index"
  - Displays traffic light phase numbers

### Statistics Collection

The `statistics.xml` file can be configured to collect:
- Vehicle statistics (travel time, speed)
- Detector data (vehicle counts, waiting times)
- Network-wide metrics

### Custom Scenarios

To create custom traffic scenarios:

1. Edit network using netedit
2. Generate routes with specific density parameters
3. Update `simulation.sumocfg` to point to new files
4. Run simulation with algorithms
