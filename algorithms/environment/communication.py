from .settings import TLS_IDS


class StateBus:
    def __init__(self) -> None:
        self.states = {}  # {agent_id: state}


    def publish(self, agent_id: str, state: tuple[int, ...]) -> None:
        # publish state to bus
        self.states[agent_id] = state

    
    def read(self, agent_id: str) -> dict[str, tuple[int, ...]]:
        # return the states of the adjacent agents
        return {
            a: self.states.get(a, ()) for a in TLS_IDS[agent_id]['adjacent']
        }