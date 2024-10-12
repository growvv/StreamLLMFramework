from .agent import Agent, AssistAgent
from typing import List
from flask_socketio import SocketIO
from .handler_agent import TextHandlerAgent, ImageHandlerAgent, LoggingHandlerAgent, DataFilterHandlerAgent, ForwardingHandlerAgent

class AgentStore:
    """
    AgentStore类，用于管理所有的Agent，实现Agent的可插拔性。
    """
    def __init__(self, socketio: SocketIO = None):
        self.agents = {}
        self.agent_categories = [
            "AssistAgent", 
            "TextHandlerAgent", 
            "ImageHandlerAgent", 
            "LoggingHandlerAgent", 
            "DataFilterHandlerAgent", 
            "ForwardingHandlerAgent"
        ]
        self.socketio = socketio

    def __create_agent_helper(self, **kwargs) -> Agent:
        name = kwargs.get("name")
        category = kwargs.get("category")
        print(kwargs)
        if category == "AssistAgent":
            llm_type = kwargs.get("llm_type")
            if llm_type is None:
                raise ValueError("llm_type is required for AssistAgent")
            return AssistAgent(name=name, llm_type=llm_type, socketio=self.socketio)
        elif category == "TextHandlerAgent":
            return TextHandlerAgent(name=name, socketio=self.socketio)
        elif category == "ImageHandlerAgent":
            return ImageHandlerAgent(name=name, socketio=self.socketio)
        elif category == "LoggingHandlerAgent":
            return LoggingHandlerAgent(name=name, socketio=self.socketio)
        elif category == "DataFilterHandlerAgent":
            keyword = kwargs.get("keyword")
            if keyword is None:
                raise ValueError("keyword is required for DataFilterHandlerAgent")
            return DataFilterHandlerAgent(name=name, keyword=keyword, socketio=self.socketio)
        elif category == "ForwardingHandlerAgent":
            target_stream_name = kwargs.get("target_stream")
            target_stream = self.get_agent(target_stream_name)
            if target_stream is None:
                raise ValueError(f"Target stream {target_stream_name} not found")
            return ForwardingHandlerAgent(name=name, target_stream=target_stream, socketio=self.socketio)
        else:
            raise ValueError(f"Unknown agent category: {category}")


    def get_agent(self, agent_name: str) -> Agent:
        return self.agents.get(agent_name)

    def create_agent(self, **kwargs) -> Agent:
        name = kwargs.get("name")
        category = kwargs.get("category")
        if category not in self.agent_categories:
            raise ValueError(f"Unknown agent category: {category}")
        try:
            agent = self.__create_agent_helper(**kwargs)
            self.add_agent(agent)
            return agent
        except ValueError as e:
            raise ValueError(f"Failed to create agent {name}: {e}")

    def add_agent(self, agent: Agent):
        if agent.name in self.agents:
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
    