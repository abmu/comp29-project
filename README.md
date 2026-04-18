# comp29-project

**Investigating the use of Decentralised Reinforcement Learning Algorithms in Traffic Environments**

This was completed for the COMP0029 Final Year Project module during my BSc Computer Science studies at UCL, supervised under Prof. [Graham Roberts](https://profiles.ucl.ac.uk/6880-graham-roberts).

[comp29-project.webm](https://github.com/user-attachments/assets/1f066275-254d-4d5c-9413-c2e54336b42b)

## Quick Overview

| Folder | Purpose |
|--------|---------|
| **[simulation/](simulation/)** | Simulated traffic environment |
| **[algorithms/](algorithms/)** | Reinforcement learning agents (QL, DQN, CDQN) |
| **[thesis/](thesis/)** | Academic report with results and analysis |

## Getting Started

Please refer to the `README.md` files in the respective folders for more details.

### How They Work Together

1. **Simulation Setup**: Generate traffic routes using `simulation/scripts/batch.py`.
2. **Training**: Train algorithms in `algorithms/run.py` on the generated traffic routes.
3. **Evaluation**: Test trained models on new routes with different traffic densities.
4. **Analysis**: Results stored in `algorithms/results/` and summarised in `thesis/project_report.pdf`.

### Example Setup

Note: you may want to change the model training/evaluation settings, or change the traffic environment network.

```bash
# 1. Generate routes
cd simulation/scripts && python batch.py

# 2. Train/evaluate algorithms
cd ../../algorithms && python run.py

# 3. Analyze results
cd results && python results.py
```
