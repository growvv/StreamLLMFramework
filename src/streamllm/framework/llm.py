from openai import OpenAI
from zhipuai import ZhipuAI
import os

# 全局的 API keys 字典
llm_api_keys = {
    'openai': os.getenv("OPENAI_API_KEY"),
    'zhipu': os.getenv("ZHIPU_API_KEY"),
    'qwen': os.getenv("QWEN_API_KEY")
}

class LLMQueryClient:
    def __init__(self, provider: str):
        self.provider = provider
        self.llm_api_key = llm_api_keys.get(provider)
        if not self.llm_api_key:
            raise ValueError(f"API key for LLM type '{provider}' not found.")

    def query_llm(self, prompt: str) -> str:
        print(f"Client querying {self.provider} LLM with prompt: {prompt}")
        
        if self.provider == "openai":
            return self._query_openai(prompt)
        elif self.provider == "zhipu":
            return self._query_zhipu(prompt)
        elif self.provider == "qwen":
            return self._query_qwen(prompt)
        else:
            return "Unsupported LLM provider."

    def _query_openai(self, prompt: str) -> str:
        try:
            client = OpenAI(api_key=self.llm_api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7,
                n=1,
                stop=None
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"An error occurred with OpenAI: {e}"

    def _query_zhipu(self, prompt: str) -> str:
        try:
            client = ZhipuAI(api_key=self.llm_api_key) # 填写您自己的APIKey
            response = client.chat.completions.create(
                model="glm-4-plus",  # 填写需要调用的模型编码
                messages=[
                    {"role": "system", "content": "你是一个乐于解答各种问题的助手，你的任务是为用户提供专业、准确、有见地的建议。"},
                    {"role": "user", "content": prompt}
                ],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"An error occurred with Zhipu: {e}"

    def _query_qwen(self, prompt: str) -> str:
        # Placeholder for Qwen API integration
        try:
            # Implement Qwen API call here
            return "Qwen response"
        except Exception as e:
            return f"An error occurred with Qwen: {e}"
        
if __name__ == "__main__":
    client = LLMQueryClient(provider="openai")
    response = client.query_llm("请介绍一下 Python 的装饰器。")
    print("OpenAI response:", response)
    
    client = LLMQueryClient(provider="zhipu")
    response = client.query_llm("请介绍一下 Python 的装饰器。")
    print("ZhipuAI response:", response)
    
    client = LLMQueryClient(provider="qwen")
    response = client.query_llm("请介绍一下 Python 的装饰器。")
    print("Qwen response:", response)
    
    client = LLMQueryClient(provider="unknown")
    response = client.query_llm("请介绍一下 Python 的装饰器。")
    print("Unknown provider response:", response)