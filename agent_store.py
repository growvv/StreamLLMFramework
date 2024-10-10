from agent import Agent
from typing import List
from flask_socketio import SocketIO

class AgentStore:
    """
    AgentStore类，用于管理所有的Agent，实现Agent的可插拔性。
    """
    def __init__(self, socketio: SocketIO = None):
        self.agents = {}
        self.socketio = socketio

    def create_agent(self, name: str, llm_type: str) -> Agent:
        if name in self.agents:
            print(f"Agent {name} already exists in the store.")
            return self.agents.get(name)
        agent = Agent(name=name, llm_type=llm_type, socketio=self.socketio)
        self.add_agent(agent)
        return agent

    def add_agent(self, agent: Agent):
        if agent.name in self.agents:
            # raise ValueError(f"Agent {agent.name} already exists in the store.")
            print(f"Agent {agent.name} already exists in the store.")
            return
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

    def list_agents(self):
        return list(self.agents.values())