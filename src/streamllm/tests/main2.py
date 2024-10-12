from streamllm import StreamManager
from streamllm import AssistAgent
from streamllm import AgentStore
from streamllm import TextHandlerAgent, ImageHandlerAgent, ForwardingHandlerAgent

# 使用框架
if __name__ == "__main__":
    # 初始化 StreamManager 和 AgentStore
    stream_manager = StreamManager()
    agent_store = AgentStore()

    # 创建 Streams
    text_stream = stream_manager.create_stream("text_stream")
    image_stream = stream_manager.create_stream("image_stream")
    analytics_stream = stream_manager.create_stream("analytics_stream")  # 新增一个分析流

    # 创建 Agents
    agent1 = AssistAgent(name="Agent1", llm_type="qwen")
    agent2 = AssistAgent(name="Agent2", llm_type="qwen")
    agent3 = AssistAgent(name="Agent3", llm_type="qwen")  # 新增一个Agent

    # 添加 Agents 到 AgentStore
    agent_store.add_agent(agent1)
    agent_store.add_agent(agent2)
    agent_store.add_agent(agent3)


    # 注册 Handlers 和 Agents 到 Streams
    text_handler_agent = TextHandlerAgent("TextHandler")
    text_handler_agent.subscribe(text_stream)
    text_stream.register_handler(agent1.process_data)
    text_stream.register_handler(agent2.process_data)

    image_handler_agent = ImageHandlerAgent("ImageHandler")
    image_handler_agent.subscribe(image_stream)
    image_stream.register_handler(agent1.process_data)

    # 设置流之间的连接：text_stream -> analytics_stream
    forwarding_handler_agent = ForwardingHandlerAgent("ForwardingHandler", analytics_stream)
    forwarding_handler_agent.subscribe(text_stream)

    # 在 analytics_stream 注册 Agent3 处理数据
    analytics_stream.register_handler(agent3.process_data)

    # 模拟数据流
    text_stream.emit("这是一个测试文本。")
    with open("example.jpg", "rb") as f:
        image_data = f.read()
        image_stream.emit(image_data)