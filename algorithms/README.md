# Algorithms

This folder contains implementations of various reinforcement learning algorithms for controlling traffic lights in a simulated urban environment using SUMO (Simulation of Urban MObility). The project implements single-agent and multi-agent approaches for traffic light control optimization.

## Overview

The algorithms are designed to control traffic lights at junctions to minimize vehicle waiting times, reduce congestion, and optimise traffic flow. The system supports different network topologies (demo, crossing, extended) with varying numbers of traffic light agents.

### Key Features

- **Multiple Algorithms**: Fixed Timer (baseline), Q-Learning, Deep Q-Learning, and Communicative Deep Q-Learning
- **State Compression**: Three levels of state space compression to handle large state spaces
- **Multi-Agent Support**: Coordination between multiple traffic lights via communication
- **SUMO Integration**: Real-time simulation with realistic traffic dynamics
- **Evaluation Framework**: Comprehensive evaluation and result analysis tools

## Dependencies

### Required Software
- **SUMO** (Simulation of Urban MObility) - Traffic simulation software
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

## Project Structure

```
algorithms/
├── agent.py                 # Base agent classes and interfaces
├── comm_deep_q_learning.py  # Communicative Deep Q-Learning implementation
├── deep_q_learning.py       # Deep Q-Learning implementation
├── fixed_timer.py           # Fixed timer baseline algorithm
├── network.py               # Multi-agent network coordination
├── q_learning.py            # Q-Learning implementation
├── run.py                   # Main execution script
├── utils.py                 # Utility functions
├── environment/             # Environment interfaces
│   ├── __init__.py
│   ├── action.py            # Action space definitions
│   ├── communication.py     # Inter-agent communication
│   ├── reward.py            # Reward function calculations
│   ├── route.py             # Route management
│   ├── settings.py          # SUMO network configurations
│   ├── state.py             # State representation and compression
│   └── utils.py             # Environment utilities
└── results/                 # Result processing and analysis
    ├── format.py            # Result formatting utilities
    └── results.py           # Result analysis and plotting
```

## Usage

### Running the Algorithms

1. **Configure the simulation** in `run.py`:
   ```python
   NET_NAME = 'demo'  # Choose: 'demo', 'crossing', 'extended'
   MODE = 'train'     # 'train' or 'eval'
   ```

2. **Execute the training/evaluation**:
   ```bash
   cd algorithms
   python run.py
   ```

### Network Configurations

- **demo**: Single junction (CJ_1) with 4 approaches
- **crossing**: Single junction (CJ_2) with pedestrian crossing
- **extended**: Three junctions (CJ_1, CJ_2, CJ_9) requiring coordination

### Algorithm Variants

Each algorithm supports different compression levels (c0, c1, c2) for state space reduction:

- **c0**: No compression (full state)
- **c1**: Moderate compression
- **c2**: High compression

## Implemented Algorithms

### 1. Fixed Timer (FT)
**File**: `fixed_timer.py`

A baseline algorithm that cycles through predefined traffic light phases with fixed durations. No learning involved.

**Key Features**:
- Fixed action sequence: [0,0,0,3,3,3,6]
- Collects statistics (cache stats) for reward weight calculation
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
- Neural network with ReLU activations and the Adam optimiser
- Experience replay buffer (capacity: 16,384)
- Target network for stable learning

**Network Architecture**:
- Input: State vector (size depends on compression)
- Hidden layers: 64 -> 64 neurons
- Output: Q-values for each action

**Hyperparameters**:
- Learning rate: 0.0005
- Batch size: 64
- Target update frequency: 72,000 steps
- Discount factor (γ): 0.9

### 4. Communicative Deep Q-Learning (CDQN)
**File**: `comm_deep_q_learning.py`

Multi-agent extension of DQN with inter-agent communication.

**Key Features**:
- State sharing between neighboring agents
- Enhanced network architecture for neighbor state processing
- StateBus for communication coordination

**Network Architecture**:
- Input: Local state + neighbor states
- Hidden layers: 256 → 128 → 64 → action_dim
- Processes concatenated state information

## Environment Interface

### State Representation
**File**: `environment/state.py`

States are represented as tuples containing:
- Vehicle queue lengths (discretized: 0-3 levels)
- Pedestrian waiting times
- Current traffic light phase

**Compression Levels**:
- **C0**: Raw counts, full resolution
- **C1**: Moderate discretization
- **C2**: High discretization (coarser bins)

### Action Space
**File**: `environment/action.py`

Available actions correspond to traffic light phases:
- **0**: North-South green
- **3**: East-West green  
- **6**: Pedestrian crossing

Each action has associated minimum durations and phase transition sequences.

### Reward Function
**File**: `environment/reward.py`

Reward combines multiple objectives:
- Negative vehicle waiting times
- Negative pedestrian waiting times
- Vehicle throughput
- Pedestrian throughput

**Components**:
- Vehicle delay penalty
- Pedestrian delay penalty
- Throughput bonuses
- Emergency penalty: -1000 (for invalid states)

### Communication
**File**: `environment/communication.py`

Implements StateBus for multi-agent communication:
- Agents publish their current states
- Agents read neighbor states
- Supports dynamic neighbor relationships

## Results and Analysis

### Output Structure
Results are saved in `results/{NET_NAME}/{MODE}/`:
- `{algorithm}.txt`: Episode reward lists
- `time.txt`: Total execution time
- Model files: `{algorithm}_model__c{compression}__{tls_id}.pt`
- Q-tables: `q_table__c{compression}__{tls_id}.txt`

### Analysis Tools

**results.py**: 
- Moving average smoothing
- Outlier removal
- Performance comparison plots

**format.py**:
- Result formatting and export
- Statistical summaries

### Example Results
The `results/` folder contains pre-computed results for different algorithms and networks, including:
- Training curves
- Evaluation metrics
- Model checkpoints

## Configuration

### SUMO Settings
**File**: `environment/settings.py`

Defines network topologies and detector configurations:
- Traffic light IDs and their properties
- Lane detector placements
- Induction loop positions
- Adjacent junction relationships

### Simulation Parameters
- Simulation time: 3600 seconds
- Step length: 1.0 second
- Total steps: 3600