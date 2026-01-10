class StateBus:
    def __init__(self) -> None:
        self.states = {}  # {agent_id: state}


    def publish(self, agent_id: str, state: tuple[int, ...]) -> None:
        # publish state to bus
        self.states[agent_id] = state

    
    def 