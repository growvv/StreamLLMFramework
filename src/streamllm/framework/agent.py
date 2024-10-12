from openai import OpenAI
from typing import Any
from flask_socketio import SocketIO
from .llm import LLMQueryClient
from .stream import Stream

class Agent:
    def __init__(self, name: str, socketio: SocketIO=None):
        self.category = "Agent"
        self.name = name
        self.socketio = socketio
        self.subscribed_streams = []

    def process_data(self, data: Any):
        raise NotImplementedError("Subclasses should implement this method")
    
    def subscribe(self, stream: Stream):
        self.subscribed_streams.append(stream)
        stream.register_handler(self.process_data)

    def unsubscribe(self, stream: Stream):
        if stream in self.subscribed_streams:
            self.subscribed_streams.remove(stream)
            stream.unregister_handler(self.process_data)
    
    def handle_response(self, response: str):
        print(f"Agent {self.name} received response: {response}")
        # 进一步处理响应，如存储、触发其他操作等
        
        # 向前端发送处理结果
        if self.socketio:
            self.socketio.emit('agent_response', {
                'agent': self.name,
                'response': response
            })

class PromptAgent(Agent):
    """
    Agent 类代表一个能够与 LLM 交互的实体。它可以通过提示（prompt）向 LLM 发起查询，并处理 Stream 中的数据。
    每个 Agent 可以订阅一个或多个 Stream，并基于收到的数据进行相应的处理。
    """
    def __init__(self, name: str, llm_type: str, socketio: SocketIO=None):
        super().__init__(name, socketio)
        self.category = "PromptAgent"
        self.llm_type = llm_type
        self.socketio = socketio
        self.client = LLMQueryClient(provider=self.llm_type)

    def process_data(self, data: Any):
        prompt = self.generate_prompt(data)
        response = self.query_llm(prompt)
        self.handle_response(response)

    def generate_prompt(self, data: Any) -> str:
        # 根据数据生成提示
        if isinstance(data, str):
            return f"请分析以下文本数据并提供见解：{data}"
        elif isinstance(data, bytes):
            return f"请分析以下图像数据并描述其内容。"
        else:
            return f"收到数据：{data}"

    def query_llm(self, prompt: str) -> str:
        print(f"Agent {self.name} querying LLM with prompt: {prompt}")

        try:
            response = self.client.query_llm(prompt)
            return response
        except Exception as e:
            return f"An error occurred: {e}"

class AssistAgent(PromptAgent):
    """
    AssistAgent 类代表一个能够与 LLM 交互的实体。它可以通过提示（prompt）向 LLM 发起查询，并处理 Stream 中的数据。
    每个 Agent 可以订阅一个或多个 Stream，并基于收到的数据进行相应的处理。
    """
    def __init__(self, name: str, llm_type: str, socketio: SocketIO=None):
        super().__init__(name, llm_type, socketio=socketio)
        self.category = "AssistAgent"

    def generate_prompt(self, data: Any) -> str:
        # 根据数据生成提示
        if isinstance(data, str):
            return f"我是一个乐于解答各种问题的助手，您可以问我任何问题。"
        elif isinstance(data, bytes):
            return f"我是一个乐于解答各种问题的助手，可以处理图像数据。"
        else:
            return f"收到数据：{data}"