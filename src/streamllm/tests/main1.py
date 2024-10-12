from streamllm.framework.handler_agent import TextHandlerAgent, ImageHandlerAgent
from streamllm.framework.agent import AssistAgent
from streamllm.framework.stream_manager import StreamManager
from streamllm.framework.stream import Stream

# 创建Agents
agent1 = AssistAgent(name="DataAnalyzer", llm_type="qwen")
agent2 = AssistAgent(name="MaintanceAnalyzer", llm_type="qwen")
text_handler_agent = TextHandlerAgent("TextHandler")
image_handler_agent = ImageHandlerAgent("ImageHandler")

stream_manager = StreamManager()
text_stream = stream_manager.create_stream("text")
image_stream = stream_manager.create_stream("image")

# 注册Agent的处理函数到Stream
text_stream.register_handler(agent1.process_data)
text_stream.register_handler(agent2.process_data)

# 注册处理器到Stream
text_handler_agent.subscribe(text_stream)
image_handler_agent.subscribe(image_stream)

# 模拟数据流
text_stream.emit("协同处理的文本数据。")
# with open("example.jpg", "rb") as f:
#     image_data = f.read()
#     image_stream.emit(image_data)

# 取消注册处理器
text_handler_agent.unsubscribe(text_stream)
image_handler_agent.unsubscribe(image_stream)

