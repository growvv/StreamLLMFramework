from PIL import Image
import io
from typing import Any, Callable
from .stream_manager import StreamManager
from .stream import Stream
from .agent import Agent

"""
为了支持多模态数据处理，Stream 可以根据数据类型将数据分发给不同的 Handler。
例如，可以为文本、图像、音频等不同类型的数据注册不同的处理器。
"""

def text_handler(data: str):
    print(f"Text Handler processing data: {data}")

def image_handler(data: bytes):
    try:
        image = Image.open(io.BytesIO(data))
        print(f"[Image Handler] Received image with size: {image.size}")
    except Exception as e:
        print(f"[Image Handler] Failed to process data: {e}")

def logging_handler(data: Any):
    print(f"[Logging Handler] Data: {data}")

def data_filter_handler_factory(keyword: str) -> Callable[[Any], None]:
    def handler(data: Any):
        if isinstance(data, str) and keyword in data:
            print(f"[Data Filter Handler] '{keyword}' found in data: {data}")
    handler.__name__ = f"data_filter_handler_{keyword}"
    return handler

# 创建一个专门的Handler，将数据转发到目标流。
def forwarding_handler_factory(target_stream: Stream) -> Callable[[Any], None]:
    def handler(data: Any):
        print(f"Forwarding handler forwarding data to stream {target_stream.name}: {data}")
        target_stream.emit(data)
    return handler

def agent_handler_factory(agent: Agent) -> Callable[[Any], None]:
    def handler(data: Any):
        agent.process_data(data)
    handler.__name__ = f"agent_handler_{agent.__name__}_{agent.name}"
    return handler

__all__ = ["text_handler", "image_handler", "logging_handler", "data_filter_handler_factory", "forwarding_handler_factory", "agent_handler_factory"]

