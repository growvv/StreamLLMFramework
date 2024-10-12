from PIL import Image
import io
from typing import Any
from .stream import Stream
from .agent import Agent
from flask_socketio import SocketIO

"""
为了支持多模态数据处理，Stream 可以根据数据类型将数据分发给不同的 HandlerAgent
例如，可以为文本、图像、音频等不同类型的数据注册不同的处理器。
"""

class TextHandlerAgent(Agent):
    def __init__(self, name: str, socketio : SocketIO = None):
        super().__init__(name=name, socketio=socketio)
        self.category = "TextHandlerAgent"

    def process_data(self, data: str):
        print(f"Text Handler processing data: {data}")
        self.handle_response(f"Processed text data: {data}")

class ImageHandlerAgent(Agent):
    def __init__(self, name: str, socketio : SocketIO = None):
        super().__init__(name=name, socketio=socketio)
        self.category = "ImageHandlerAgent"

    def process_data(self, data: bytes):
        try:
            image = Image.open(io.BytesIO(data))
            print(f"[Image Handler] Received image with size: {image.size}")
        except Exception as e:
            print(f"[Image Handler] Failed to process data: {e}")

        self.handle_response(f"Processed image data: {data}")

class LoggingHandlerAgent(Agent):
    def __init__(self, name: str, socketio : SocketIO = None):
        super().__init__(name=name, socketio=socketio)
        self.category = "LoggingHandlerAgent"

    def process_data(self, data: Any):
        print(f"[Logging Handler] Data: {data}")
        self.handle_response(f"Logged data: {data}")

class DataFilterHandlerAgent(Agent):
    def __init__(self, name: str, keyword: str, socketio : SocketIO = None):
        super().__init__(name=name, socketio=socketio)
        self.category = "DataFilterHandlerAgent"
        self.keyword = keyword

    def process_data(self, data: Any):
        if isinstance(data, str) and self.keyword in data:
            print(f"[Data Filter Handler] '{self.keyword}' found in data: {data}")
        self.handle_response(f"Filtered data: {data}")

class ForwardingHandlerAgent(Agent):
    def __init__(self, name: str, target_stream: Stream, socketio : SocketIO = None):
        super().__init__(name=name, socketio=socketio)
        self.category = "ForwardingHandlerAgent"
        self.target_stream = target_stream

    def process_data(self, data: Any):
        print(f"Forwarding handler forwarding data to stream {self.target_stream.name}: {data}")
        self.target_stream.emit(data)
        self.handle_response(f"Forwarded data to stream {self.target_stream.name}")

__all__ = [ "TextHandlerAgent", "ImageHandlerAgent", "LoggingHandlerAgent", "DataFilterHandlerAgent", "ForwardingHandlerAgent" ]