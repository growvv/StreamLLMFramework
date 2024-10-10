from agent import Agent
from typing import List

class AgentStore:
    """
    AgentStore类，用于管理所有的Agent，实现Agent的可插拔性。
    """
    def __init__(self):
        self.agents = {}

    def add_agent(self, agent: Agent):
        if agent.name in self.agents:
            raise ValueError(f"Agent {agent.name} already exists in the store.")
        self.agents[agent.name] = agent
        print(f"Agent {agent.name} added to the store.")

    def remove_agent(self, agent_name: str):
        if agent_name in self.agents:
            del self.agents[agent_name]
            print(f"Agent {agent_name} removed from the store.")

    def get_agent(self, agent_name: str) -> Agent:
        return self.agents.get(agent_name)

    def get_all_agents(self) -> List[Agent]:
        return list(self.agents.values())
