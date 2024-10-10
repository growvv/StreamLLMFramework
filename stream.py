from typing import Callable, Any, List
from flask_socketio import SocketIO

class Stream:
    """
    StreamManager 负责管理所有的 Stream 实例，包括创建、查找和删除 Stream。
    它确保不同的 Stream 能够被有效地组织和访问。
    """
    def __init__(self, name: str, socketio: SocketIO):
        self.name = name
        self.handlers: List[Callable[[Any], None]] = []
        self.connected_streams: List['Stream'] = []
        self.socketio = socketio

    def register_handler(self, handler: Callable[[Any], None]):
        self.handlers.append(handler)
        print(f"Handler {handler.__name__} registered to stream {self.name}")

    def unregister_handler(self, handler: Callable[[Any], None]):
        if handler in self.handlers:
            self.handlers.remove(handler)
            print(f"Handler {handler.__name__} unregistered from stream {self.name}")
        else:
            print(f"Handler {handler.__name__} not found in stream {self.name}")

    def emit(self, data: Any):
        # 优化输出
        if isinstance(data, bytes):
            print(f"Stream {self.name} emitting data: <bytes>")
        elif isinstance(data, str):
            print(f"Stream {self.name} emitting data: {data}")
        else:
            print(f"Stream {self.name} emitting data: <unknown>")

        # 向前端发送数据流事件
        if self.socketio:
            self.socketio.emit('data_flow', {
                'stream': self.name,
                'data': str(data),
                'action': 'emit'
            })

        for handler in self.handlers:
            handler(data)

        # 将数据传递到连接的流 (和 forward功能有重叠)
        for stream in self.connected_streams:
            print(f"Stream {self.name} forwarding data to stream {stream.name}")

            if self.socketio:
                self.socketio.emit('data_flow', {
                    'stream': self.name,
                    'target_stream': stream.name,
                    'data': str(data),
                    'action': 'forward'
                })

            stream.emit(data)

    def clear_handlers(self):
        self.handlers.clear()
        print(f"All handlers cleared from stream {self.name}")

    """
    Stream类增加了连接其他流的功能，使得一个流可以将数据传递到另一个流。
    新增的方法包括connect_stream和disconnect_stream，用于管理流之间的连接。
    """
    def connect_stream(self, stream: 'Stream'):
        if stream not in self.connected_streams:
            self.connected_streams.append(stream)
            print(f"Stream {self.name} connected to stream {stream.name}")

    def disconnect_stream(self, stream: 'Stream'):
        if stream in self.connected_streams:
            self.connected_streams.remove(stream)
            print(f"Stream {self.name} disconnected from stream {stream.name}")