from stream import Stream
from typing import Any

class StreamManager:
    """
    Stream 类负责管理一个数据流，并允许注册多个处理器（Handlers）来处理进入的数据。
    每个 Stream 可以接收不同类型的数据（如文本、图像等），并将其分发给相应的 Handler。
    """
    def __init__(self):
        self.streams = {}

    def create_stream(self, name: str) -> Stream:
        if name in self.streams:
            raise ValueError(f"Stream {name} already exists.")
        stream = Stream(name)
        self.streams[name] = stream
        print(f"Stream {name} created.")
        return stream

    def get_stream(self, name: str) -> Stream:
        if name not in self.streams:
            return self.create_stream(name)
        return self.streams.get(name)

    def delete_stream(self, name: str):
        if name in self.streams:
            del self.streams[name]
            print(f"Stream {name} deleted.")
