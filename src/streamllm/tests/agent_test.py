from streamllm.framework.agent import AssistAgent

if __name__ == "__main__":
    agent = AssistAgent(name="DataAnalyzer", llm_type="qwen")
    data = "一个数列的前四项是 1, 2, 3, 5，求第 10 项。"
    agent.process_data(data)