from streamllm import StreamManager
from streamllm import TextHandlerAgent, ImageHandlerAgent

if __name__ == "__main__":
    stream_manager = StreamManager()
    text_stream = stream_manager.create_stream("text")
    image_stream = stream_manager.create_stream("image")
    text_handler_agent = TextHandlerAgent("TextHandler")
    image_handler_agent = ImageHandlerAgent("ImageHandler")

    text_handler_agent.subscribe(text_stream)
    image_handler_agent.subscribe(image_stream)

    # 模拟数据流
    text_stream.emit("This is a text message.")
    with open("example.jpg", "rb") as f:
        image_data = f.read()
        # image_stream.emit(image_data)

    # 取消注册处理器
    text_handler_agent.unsubscribe(text_stream)
    text_stream.emit("Another text message.")