import yaml
from stream_manager import StreamManager
from agent import Agent
from handler import text_handler, image_handler, forwarding_handler_factory, agent_handler_factory
from agent_store import AgentStore

# DSL解析器
class DSLParser:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.stream_manager = StreamManager()
        self.agent_store = AgentStore()
        self.handlers_map = {
            "text_handler": text_handler,
            "image_handler": image_handler,
            # "agent_handler" will be handled separately
            "forwarding_handler": forwarding_handler_factory
        }

    def parse(self):
        with open(self.config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)

        # 创建Streams
        # 遍历配置中的 streams，为每个流创建 Stream 实例，并注册相应的处理器。
        for stream_conf in config.get('streams', []):
            if not self.stream_manager.get_stream(stream_conf['name']):
                stream = self.stream_manager.create_stream(stream_conf['name'])
            for handler_conf in stream_conf.get('handlers', []):
                handler_type = handler_conf['type']
                if handler_type == "agent_handler":
                    # Agent handlers will be connected after Agents are created
                    pass
                elif handler_type == "forwarding_handler":
                    target_stream_name = handler_conf['target']
                    target_stream = self.stream_manager.get_stream(target_stream_name)
                    if not target_stream:
                        target_stream = self.stream_manager.create_stream(target_stream_name)
                    handler = forwarding_handler_factory(target_stream)
                    stream.register_handler(handler)
                else:
                    handler = self.handlers_map.get(handler_type)
                    if handler:
                        stream.register_handler(handler)
                    else:
                        print(f"Unknown handler type: {handler_type}")

        # 创建Agents
        for agent_conf in config.get('agents', []):
            agent = Agent(name=agent_conf['name'], llm_type=agent_conf['llm_type'])
            self.agent_store.add_agent(agent)

        # 注册Agent Handlers
        # 根据每个Agent订阅的流，将对应的处理器注册到相应的流。
        # 既可以是Stream处理函数，也可以是Agent订阅Stream再处理
        for agent_conf in config.get('agents', []):
            agent = self.agent_store.get_agent(agent_conf['name'])
            if not agent:
                continue
            for stream_name in agent_conf.get('subscribed_streams', []):
                stream = self.stream_manager.get_stream(stream_name)
                if stream:
                    handler = agent_handler_factory(agent)  # 根据配置选择同步或异步处理器
                    stream.register_handler(handler)

    def get_stream_manager(self) -> StreamManager:
        return self.stream_manager

    def get_agent_store(self) -> AgentStore:
        return self.agent_store