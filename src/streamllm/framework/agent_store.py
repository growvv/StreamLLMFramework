from .agent import Agent, AssistAgent
from typing import List
from flask_socketio import SocketIO


class AgentStore:
    """
    AgentStore类，用于管理所有的Agent，实现Agent的可插拔性。
    """
    def __init__(self, socketio: SocketIO = None):
        self.agents = {}
        self.agent_categories = ["AssistAgent", "xxAgent"]
        self.socketio = socketio

    def __create_agent_helper(self, name: str, category: str, **kwargs) -> Agent:
        if category == "AssistAgent":
            llm_type = kwargs.get("llm_type")
            if llm_type is None:
                raise ValueError("llm_type is required for AssistAgent")
            return AssistAgent(name=name, llm_type=llm_type, socketio=self.socketio)
        elif category == "xxAgent":
            pass
        else:
            raise ValueError(f"Unknown agent category: {category}")


    def get_agent(self, agent_name: str) -> Agent:
        return self.agents.get(agent_name)

    def create_agent(self, name: str, category: str, **kwargs) -> Agent:
        if name in self.agents:
            print(f"Agent {name} already exists in the store.")
            return self.agents.get(name)
        if category not in self.agent_categories:
            raise ValueError(f"Unknown agent category: {category}")
        try:
            agent = self.__create_agent_helper(name, category, **kwargs)
            self.add_agent(agent)
            return agent
        except ValueError as e:
            raise ValueError(f"Failed to create agent {name}: {e}")

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

    def get_all_agents(self) -> List[Agent]:
        return list(self.agents.values())

    def list_agents(self):
        return list(self.agents.values())

    def list_agent_categories(self):
        return self.agent_categories
    