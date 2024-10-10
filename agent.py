from openai import OpenAI
from llm import LLMQueryClient
from typing import Any
from flask_socketio import SocketIO


class Agent:
    """
    Agent 类代表一个能够与 LLM 交互的实体。它可以通过提示（prompt）向 LLM 发起查询，并处理 Stream 中的数据。
    每个 Agent 可以订阅一个或多个 Stream，并基于收到的数据进行相应的处理。
    """
    def __init__(self, name: str, llm_type: str, socketio: SocketIO=None):
        self.name = name
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
        print(f"Agent {self.name} asynchronously querying LLM with prompt: {prompt}")

        try:
            response = self.client.query_llm(prompt)
            return response
        except Exception as e:
            return f"An error occurred: {e}"

    def handle_response(self, response: str):
        print(f"Agent {self.name} received response: {response}")
        # 进一步处理响应，如存储、触发其他操作等
        
        # 向前端发送处理结果
        if self.socketio:
            self.socketio.emit('agent_response', {
                'agent': self.name,
                'response': response
            })

if __name__ == "__main__":
    agent = Agent(name="DataAnalyzer", llm_type="zhipu")
    data = "一个数列的前四项是 1, 2, 3, 5，求第 10 项。"
    agent.process_data(data)