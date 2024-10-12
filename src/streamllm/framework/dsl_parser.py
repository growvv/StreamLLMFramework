from copy import deepcopy
import yaml
from typing import Dict, Union, List, Tuple
from .stream_manager import StreamManager
from .agent_store import AgentStore
from .agent import Agent
from .stream import Stream

Node = Union[Stream, Agent]
Link = Tuple[Node, Node]

# DSL解析器
class DSLParser:
    def __init__(self, config_path: str = "config.yaml", stream_manager: StreamManager = None, agent_store: AgentStore = None):
        self.config_path = config_path
        if stream_manager:
            self.stream_manager = stream_manager
        else:
            self.stream_manager = StreamManager()
        if agent_store:
            self.agent_store = agent_store
        else:
            self.agent_store = AgentStore()
        self.nodes = []   # 存储所有节点, 包括Stream和Agent
        self.links = []    # 存储所有边, 用于构建拓扑图, 包括Stream-Stream, Stream-Agent

        # 读取配置文件
        with open(self.config_path, 'r', encoding='utf-8') as file:
            initconfig = yaml.safe_load(file)
            self.config = deepcopy(initconfig)

    def parse(self) -> Tuple[List[Node], List[Link]]:
        # 创建Streams
        # 遍历配置中的 streams，为每个流创建 Stream 实例，并注册相应的处理器。
        for stream_conf in self.config.get('streams', []):
            stream = self.stream_manager.get_stream(stream_conf['name'])
            if not stream:
                stream = self.stream_manager.create_stream(stream_conf['name'])
                # nodes.push({id: agentName, type: 'agent'});
                self.nodes.append({'id': stream.name, 'type': 'stream'})

            # connection stream
            connections = stream_conf.get('connections', [])
            for connection in connections:
                target_stream = self.stream_manager.get_stream(connection)
                if target_stream:
                    stream.connect_stream(target_stream)
                    self.links.append({"source": stream.name, "target": target_stream.name})

        # 创建Agents
        for agent_conf in self.config.get('agents', []):
            agent = self.agent_store.get_agent(agent_conf['name'])
            if not agent:
                agent = self.agent_store.create_agent(**agent_conf)
                self.nodes.append({'id': agent.name, 'type': 'agent'})
            # self.agent_store.add_agent(agent)

        # 注册Agent Handlers
        # 根据每个Agent订阅的流，将对应的处理器注册到相应的流。
        # 既可以是Stream处理函数，也可以是Agent订阅Stream再处理
        for agent_conf in self.config.get('agents', []):
            agent = self.agent_store.get_agent(agent_conf['name'])
            if not agent:
                continue
            for stream_name in agent_conf.get('subscribed_streams', []):
                stream = self.stream_manager.get_stream(stream_name)
                if stream:  # Stream不存在, 跳过
                    agent.subscribe(stream)
                    self.links.append({"source": stream.name, "target": agent.name})

        return self.nodes, self.links

    def update_config(self, part_config: Dict):
        # 检查是否是stream更新
        if "streams" in part_config:
            for new_stream in part_config["streams"]:
                # 查找是否已有相同名称的stream
                existing_stream = next((s for s in self.config['streams'] if s['name'] == new_stream['name']), None)
                if existing_stream:
                    # 更新已有的stream
                    # existing_stream.update(new_stream)
                    pass
                else:
                    # 添加新的stream
                    self.config['streams'].append(new_stream)

        # 检查是否是agent更新
        if "agents" in part_config:
            for new_agent in part_config["agents"]:
                # 查找是否已有相同名称的agent
                existing_agent = next((a for a in self.config['agents'] if a['name'] == new_agent['name']), None)
                if existing_agent:
                    # 更新已有的agent
                    # existing_agent.update(new_agent)
                    pass
                else:
                    # 添加新的agent
                    self.config['agents'].append(new_agent)

        # 检查是否是为现有的agent添加subscribed_streams
        if "agent_subscriptions" in part_config:
            for agent_subscription in part_config["agent_subscriptions"]:
                agent_name = agent_subscription['name']
                streams_to_add = agent_subscription.get('subscribed_streams', [])
                
                # 查找对应的agent
                existing_agent = next((a for a in self.config['agents'] if a['name'] == agent_name), None)
                if existing_agent:
                    # 添加新的subscribed_streams，避免重复
                    existing_subscriptions = set(existing_agent.get('subscribed_streams', []))
                    updated_subscriptions = existing_subscriptions.union(set(streams_to_add))
                    existing_agent['subscribed_streams'] = list(updated_subscriptions)
                else:
                    print(f"Agent '{agent_name}' not found.")

        # 写回配置文件
        self.writeback_config()

    def get_config(self):
        return self.config
    
    ## 将config写回文件
    def writeback_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as file:
            yaml.dump(self.config, file,sort_keys=False)

    def get_stream_manager(self) -> StreamManager:
        return self.stream_manager

    def get_agent_store(self) -> AgentStore:
        return self.agent_store