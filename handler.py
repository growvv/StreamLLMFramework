from PIL import Image
import io
from stream_manager import StreamManager
from typing import Any, Callable
from stream import Stream
from agent import Agent

"""
为了支持多模态数据处理，Stream 可以根据数据类型将数据分发给不同的 Handler。
例如，可以为文本、图像、音频等不同类型的数据注册不同的处理器。
"""

def text_handler(data: str):
    print(f"Text Handler processing data: {data}")

def image_handler(data: bytes):
    image = Image.open(io.BytesIO(data))
    print(f"Image Handler processing image with size: {image.size}")

# 创建一个专门的Handler，将数据转发到目标流。
def forwarding_handler_factory(target_stream: Stream) -> Callable[[Any], None]:
    def handler(data: Any):
        print(f"Forwarding handler forwarding data to stream {target_stream.name}: {data}")
        target_stream.emit(data)
    return handler

def agent_handler_factory(agent: Agent) -> Callable[[Any], None]:
    def handler(data: Any):
        agent.process_data(data)
    handler.__name__ = f"agent_handler_{agent.name}"
    return handler

if __name__ == "__main__":
    stream_manager = StreamManager()
    text_stream = stream_manager.create_stream("text")
    image_stream = stream_manager.create_stream("image")

    text_stream.register_handler(text_handler)
    image_stream.register_handler(image_handler)

    # 模拟数据流
    text_stream.emit("This is a text message.")
    with open("example.jpg", "rb") as f:
        image_data = f.read()
        # image_stream.emit(image_data)

    # 取消注册处理器
    text_stream.unregister_handler(text_handler)
    text_stream.emit("Another text message.")
