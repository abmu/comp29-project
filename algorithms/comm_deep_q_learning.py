from environment import StateBus, ACTION_SPACE, get_state, get_blank_state
from deep_q_learning import DeepQLearning


class CommDeepQLearning(DeepQLearning):
    def __init__(self, tls_id: str, save_dir: str, train_mode: bool, state_bus: StateBus, compress_state: bool = False) -> None:
        super().__init__(tls_id, save_dir, train_mode, compress_state)
        self.state_bus = state_bus
        self.state_bus.publish(self.tls_id, get_blank_state(self.tls_id, self.compress_state))
        self.model_name = 'communicative_' + self.model_name


    def get_state_size(self) -> int:
        # return the input state size for the policy net
        n = len(get_blank_state(self.tls_id, self.compress_state))

        others = self.state_bus.read(self.tls_id)
        for _, s in others.items():
            n += len(s)

        return n


    def get_comm_state(self) -> tuple[int, ...]:
        # Get the joint state from the communication state bus
        state = get_state(self.conn, self.tls_id, self.compress_state)
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

        state = get_state(self.conn, self.tls_id, self.compress_state)
        self.state_bus.publish(self.tls_id, state)

        reward = self.controller.run()
        self.reward += reward
        return reward


    def finish_step(self, done: bool):
        if self.train_mode and self.controller.finished():
            next_state = self.get_comm_state()
            duration = self.controller.get_total_duration()

            # save transition
            action_id_to_idx = {aid: i for i, aid in enumerate(ACTION_SPACE.keys())}
            action_idx = action_id_to_idx[self.action]
            self.memory.push(self.state, action_idx, self.reward, next_state, duration, done)

            self.train_policy_net()
