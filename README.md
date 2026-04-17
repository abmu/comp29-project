# Decentralised Reinforcement Learning for Traffic Light Control

Research project investigating decentralised reinforcement learning for traffic light control. The project combines SUMO traffic simulation, learning algorithms, and rigorous experimental analysis.

## Quick Overview

```
simulation/    → algorithms/      → thesis/
─────────────    ────────────       ──────
SUMO networks    RL agents learn    Academic
+ routes         from simulation    report
                 + control lights
```

| Folder | Purpose | Key Files |
|--------|---------|-----------|
| **[algorithms/](algorithms/)** | Reinforcement learning agents (QL, DQN, CDQN) | `run.py`, `agent.py`, `environment/` |
| **[simulation/](simulation/)** | SUMO traffic environment (demo, crossing, extended networks) | `scripts/batch.py`, `networks/`, `simulation.sumocfg` |
| **[thesis/](thesis/)** | Academic report with results and analysis | `project_report.tex`, `data/` |

## How They Work Together

1. **Simulation Setup**: Generate traffic routes using `simulation/scripts/batch.py`
2. **Agent Training**: Algorithms in `algorithms/run.py` train on simulation
   - Load network configuration and routes
   - Agents observe traffic state via detectors
   - Control traffic lights and receive rewards
3. **Evaluation**: Test trained models on new routes with different traffic densities
4. **Analysis**: Results stored in `algorithms/results/` and summarized in thesis

## Getting Started

**See detailed documentation**:
- [algorithms/README.md](algorithms/README.md) — Algorithm implementations and usage
- [simulation/README.md](simulation/README.md) — SUMO networks and route generation
- [thesis/project_report.pdf](thesis/project_report.pdf) — Full research report

**Quick setup**:
```bash
# 1. Generate routes
cd simulation/scripts && python batch.py

# 2. Train/evaluate algorithms
cd ../../algorithms && python run.py

# 3. Analyze results
cd results && python results.py
```