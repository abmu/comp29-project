import torch
import torch.nn as nn
import torch.optim as optim
from environment import StateBus, ACTION_SPACE, get_state, get_blank_state
from deep_q_learning import ReplayBuffer, DeepQLearning


"""
    Communicative Deep Q-Network model
"""
class CDQN(nn.Module):
    def __init__(self, state_dim: int, neighbour_dim: int, action_dim: int, hidden_dim: int = 256):
        super().__init__()
        input_dim = state_dim + neighbour_dim
        self.model = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, max(int(hidden_dim/2), action_dim)),
            nn.ReLU(),
            nn.Linear(max(int(hidden_dim/2), action_dim), max(int(hidden_dim/4), action_dim)),
            nn.ReLU(),
            nn.Linear(max(int(hidden_dim/4), action_dim), action_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)


class CommunicativeDeepQLearning(DeepQLearning):
    def __init__(self, tls_id: str, save_dir: str, train_mode: bool, state_bus: StateBus, compression_level: int = 0, seed: int = 0) -> None:
        super().__init__(tls_id, save_dir, train_mode, compression_level, seed)
        self.state_bus = state_bus
        self.state_bus.publish(self.tls_id, get_blank_state(self.tls_id, self.compression_level))
        self.model_name = 'comm_' + self.model_name


    def get_state_size(self) -> tuple[int, int]:
        # return the input state size for the policy net
        state = len(get_blank_state(self.tls_id, self.compression_level))

        others = self.state_bus.read(self.tls_id)
        neighbour = 0
        for _, s in others.items():
            neighbour += len(s)

        return state, neighbour


    def initialise(self) -> None:
        # initialise neural networks
        state_size, neighbour_size = self.get_state_size()
        action_size = len(ACTION_SPACE)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = device

        self.policy_net = CDQN(state_size, neighbour_size, action_size).to(device)
        if not self.train_mode:
            self.policy_net.load_state_dict(torch.load(self.save_dir + self.model_name, map_location=self.device))
            self.policy_net.eval()
            self.t = float('inf')
            self.epsilon_min = 0

        self.target_net = CDQN(state_size, neighbour_size, action_size).to(device)
        self.target_net.load_state_dict(self.policy_net.state_dict())

        self.optimiser = optim.Adam(self.policy_net.parameters(), lr=self.learning_rate)
        self.memory = ReplayBuffer()

        self.initialised = True


    def get_comm_state(self) -> tuple[int, ...]:
        # Get the joint state from the communication state bus
        state = get_state(self.conn, self.tls_id, self.compression_level)
        others = self.state_bus.read(self.tls_id)
        comm_state = list(state)
        for _, s in others.items():
            comm_state.extend(s)

        return tuple(comm_state)


    def start_step(self):
        if self.controller.finished():
            self.state = self.get_comm_state()
            self.action = self.choose_action(self.state)
            self.reward = 0
            self.controller.set_action(self.action)


    def run(self) -> float:
        self.t += 1
        if self.train_mode and self.t % self.target_update == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
            # print("Target network updated")

        state = get_state(self.conn, self.tls_id, self.compression_level)
        self.state_bus.publish(self.tls_id, state)

        reward = self.controller.run()
        self.reward += reward
        return reward


    def finish_step(self, done: bool):
        if self.train_mode and self.controller.finished() and self.controller.initialised:
            next_state = self.get_comm_state()
            duration = self.controller.get_total_duration()

            # save transition
            action_id_to_idx = {aid: i for i, aid in enumerate(ACTION_SPACE.keys())}
            action_idx = action_id_to_idx[self.action]
            self.memory.push(self.state, action_idx, self.reward, next_state, duration, done)

            self.train_policy_net()
