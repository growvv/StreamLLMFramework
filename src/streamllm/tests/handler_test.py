from streamllm.framework.stream_manager import StreamManager
from streamllm.framework.handler import text_handler, image_handler

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