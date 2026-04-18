# Algorithms

This folder contains implementations of various reinforcement learning algorithms for controlling traffic lights in a simulated urban environment using SUMO. The project implements single-agent and multi-agent approaches for traffic light control optimization.

## Overview

The algorithms are designed to control traffic lights at junctions to minimise vehicle waiting times and optimise traffic throughput. The system supports different network topologies (demo, crossing, extended).

### Key Features

- **Agent Algorithms**: Fixed Timer (baseline), Q-Learning, Deep Q-Learning, and Communicative Deep Q-Learning.
- **Environment Integration**: Real-time SUMO simulation with varying traffic dynamics.
- **Evaluation Framework**: Comprehensive evaluation and result analysis tools.

## Structure

```
algorithms/
├── agent.py                   # Base agent classes and interfaces
├── comm_deep_q_learning.py    # Communicative Deep Q-Learning implementation
├── deep_q_learning.py         # Deep Q-Learning implementation
├── fixed_timer.py             # Fixed timer baseline algorithm
├── network.py                 # Multi-agent network coordination
├── q_learning.py              # Q-Learning implementation
├── run.py                     # Main execution script
├── utils.py                   # Utility functions
├── environment/               # Environment interfaces
│   ├── __init__.py
│   ├── action.py              # Action space definitions
│   ├── communication.py       # Inter-agent communication
│   ├── reward.py              # Reward function calculations
│   ├── route.py               # Route management
│   ├── settings.py            # SUMO network configurations
│   ├── state.py               # State representation and compression
│   └── utils.py               # Environment utilities
└── results/                   # Result processing and analysis
    ├── format.py              # Result formatting utilities
    └── results.py             # Result analysis and plotting
```

## Environment

Three network topologies with traffic light system (TLS) identifiers:

- **demo**: Standard 4-way junction (CJ_1)
- **crossing**: Zebra crossing junction (CJ_2)
- **extended**: Three junctions (CJ_1, CJ_2, CJ_9)

### State Representation

**File**: `environment/state.py`

States are represented as tuples containing:
- Current traffic light phase
- Vehicle queue lengths
- Pedestrian queue lengths

Compression Levels:
- **C0**: No compression (full state)
- **C1**: Moderate compression
- **C2**: High compression

### Action Space

**File**: `environment/action.py`

Available actions correspond to traffic light phases:
- **0**: North-South green
- **3**: East-West green  
- **6**: Pedestrian crossing

Each action has associated minimum durations and phase switch sequences.

### Reward Formula

**File**: `environment/reward.py`

Reward combines multiple objectives:
- Negative vehicle waiting times
- Negative pedestrian waiting times
- Vehicle throughput
- Pedestrian throughput
- Penalty (for jams/teleportations)

### Communication

**File**: `environment/communication.py`

Implements StateBus for multi-agent communication:
- Agents publish their current states
- Agents read neighbor states

### Settings

**File**: `environment/settings.py`

Manually defines network topologies and detector configurations:
- Traffic light IDs
- Lane detector, induction loop, and crossing placements
- Neighbour relationships

Simulation Parameters
- Simulation time: 3600 seconds
- Step length: 1.0 second

## Agents

### 1. Fixed Timer (FT)
**File**: `fixed_timer.py`

A baseline algorithm that cycles through predefined traffic light phases with fixed durations. No learning involved.

**Key Features**:
- Fixed action sequence: [0,0,0,3,3,3,6]
- Collects statistics (cache stats) for reward formula weight calculation
- Deterministic behavior

### 2. Q-Learning (QL)
**File**: `q_learning.py`

Traditional tabular Q-Learning with epsilon-greedy exploration.

**Key Features**:
- Q-table with state-action pairs
- Exponential epsilon decay

**Hyperparameters**:
- Learning rate (α): 0.1
- Discount factor (γ): 0.9
- Epsilon decay: 1.5e-6

### 3. Deep Q-Learning (DQN)
**File**: `deep_q_learning.py`

Neural network-based Q-function approximation using experience replay.

**Key Features**:
- Neural network for approximation
- Experience replay buffer (capacity: 16,384)
- Target network for stable learning

**Network Architecture**:
- ReLU activations and Adam optimiser
- Input: State vector (size may vary)
- Hidden layers: 64 -> 64 neurons
- Output: Q-values for each action

**Hyperparameters**:
- Batch size: 64
- Target update frequency: 72,000 steps
- Learning rate: 0.0005
- Discount factor: 0.9

### 4. Communicative Deep Q-Learning (CDQN)
**File**: `comm_deep_q_learning.py`

Multi-agent extension of DQN with inter-agent communication.

**Key Features**:
- State sharing via a communication bus
- Extended neural network architecture

**Network Architecture**:
- Input: Local state + neighbor states
- Hidden layers: 256 → 128 → 64 neurons

## Results

Models are saved and loaded from `results/{NET_NAME}/`.

Episode rewards are saved in `results/{NET_NAME}/{MODE}/`:
- `{algorithm}.txt`: Episode reward lists
- `time.txt`: Total execution time

### Analysis Tools

**results.py**: 
- Moving average smoothing
- Outlier removal
- Comparison plots

**format.py**:
- Result formatting and export

## Example Usage

### Running the Algorithms

1. **Configure the simulation** in `run.py`:

   ```python
   NET_NAME = 'demo'   # Choose: 'demo', 'crossing', 'extended'
   MODE = 'train'      # 'train' or 'eval'
   ```

2. **Select the desired agents**:

   ```python
   NETWORKS = {
      'ft': Network(
         agents=[
               FixedTimer(
                  tls_id='CJ_1',
                  save_dir=RESULTS_DIR,
                  stats_mode=False
               )
         ],
         sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
      ),
      'ql_c2': Network(
         agents=[
               QLearning(
                  tls_id='CJ_1',
                  save_dir=RESULTS_DIR,
                  train_mode=(MODE == 'train'),
                  compression_level=2
               )
         ],
         sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
      ),
   }

   ```

3. **Execute the training/evaluation**:

   ```bash
   python run.py
   ```

## Dependencies

### Required Software
- **SUMO** (Simulation of Urban MObility)
- **Python 3.8+**

### Python Packages
- `torch` - Deep learning framework for neural networks
- `numpy` - Numerical computations
- `matplotlib` - Plotting and visualization

### Installation

1. Install SUMO:
   ```bash
   sudo apt-get install sumo
   ```

2. Install Python dependencies:
   ```bash
   pip install torch numpy matplotlib
   ```