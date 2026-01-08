import os
import sys
import uuid

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

from environment import TOTAL_STEPS, simulation_step
from runner import Runner


class Network:
    def __init__(self, agents: list[Runner], sumo_cfg: str) -> None:
        self.agents = agents
        self.sumo_cfg = sumo_cfg


    def run(self, epoch: int = 1) -> float:
        # run a single episode and return the reward
        total_reward = 0
        step = 0
        
        tid = str(uuid.uuid4())
        traci.start(self.sumo_cfg, label=tid)
        conn = traci.getConnection(tid)

        for agent in self.agents:
            agent.start_episode(conn)

        try:
            while step < TOTAL_STEPS:
                for agent in self.agents:
                    agent.start_step()

                simulation_step(conn)
                for agent in self.agents:
                    reward = agent.run()
                    total_reward += reward
                step += 1

                done = step >= TOTAL_STEPS
                for agent in self.agents:
                    agent.finish_step(done=done)

        except Exception as e:
            raise
        finally:
            conn.close()

            for agent in self.agents:
                agent.finish_episode()

        return total_reward
