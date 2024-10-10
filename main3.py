from dsl_parser import DSLParser

# 使用框架
if __name__ == "__main__":
    # 初始化 DSLParser，假设配置文件为 config.yaml
    parser = DSLParser(config_path="config.yaml")
    parser.parse()

    # 获取 StreamManager 和 AgentStore
    stream_manager = parser.get_stream_manager()
    agent_store = parser.get_agent_store()

    # 模拟数据流
    text_stream = stream_manager.get_stream("text_stream")
    image_stream = stream_manager.get_stream("image_stream")
    analytics_stream = stream_manager.get_stream("analytics_stream")

    # 发送数据
    text_stream.emit("这是一个测试文本。")
    image_stream.emit(open("example.jpg", "rb").read()) # 示例的PNG数据
