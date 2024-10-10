from agent import Agent
from stream import Stream
from stream_manager import StreamManager
from handler import text_handler, image_handler

# 创建Agents
agent1 = Agent(name="DataAnalyzer", llm_type="qwen")
agent2 = Agent(name="MaintanceAnalyzer", llm_type="qwen")

stream_manager = StreamManager()
text_stream = stream_manager.create_stream("text")
image_stream = stream_manager.create_stream("image")

# 注册Agent的处理函数到Stream
text_stream.register_handler(agent1.process_data)
text_stream.register_handler(agent2.process_data)

# 注册处理器到Stream
text_stream.register_handler(text_handler)
image_stream.register_handler(image_handler)

# 模拟数据流
text_stream.emit("协同处理的文本数据。")
# with open("example.jpg", "rb") as f:
#     image_data = f.read()
#     image_stream.emit(image_data)

# 取消注册处理器
text_stream.clear_handlers()
image_stream.clear_handlers()

