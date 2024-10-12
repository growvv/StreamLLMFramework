import eventlet
# 使用 eventlet 作为异步模式
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
from typing import Any
from streamllm import DSLParser, StreamManager, AgentStore, PromptAgent


# Flask应用和SocketIO初始化
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# 实例化StreamManager和AgentStore
stream_manager = StreamManager(socketio)
agent_store = AgentStore(socketio)

# 定义 DSLParser 实例
dsl_parser = DSLParser(config_path="config.yaml", stream_manager=stream_manager, agent_store=agent_store)

# 解析初始配置
dsl_parser.parse()
# nodes, links = dsl_parser.parse()

# 定义Flask路由
@app.route('/')
def index():
    return render_template('index.html')

### ---------- Stream 相关的 API 端点 ---------- ###
@app.route('/add_stream', methods=['POST'])
def add_stream():
    data = request.json
    stream_name = data.get('name')
    if stream_manager.get_stream(stream_name):
        return jsonify({'status': 'error', 'message': f'Stream {stream_name} already exists.'}), 400
    try:
        stream = stream_manager.create_stream(stream_name)
        return jsonify({'status': 'success', 'stream': stream.name})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/delete_stream', methods=['POST'])
def delete_stream():
    data = request.json
    stream_name = data.get('name')
    if not stream_name:
        return jsonify({'status': 'error', 'message': 'Stream name is required.'}), 400
    stream_manager.delete_stream(stream_name)
    return jsonify({'status': 'success', 'message': f'Stream {stream_name} deleted.'})

@app.route('/get_stream', methods=['GET'])
def get_stream():
    stream_name = request.args.get('name')
    if not stream_name:
        return jsonify({'status': 'error', 'message': 'Stream name is required.'}), 400
    stream = stream_manager.get_stream(stream_name)
    if not stream:
        return jsonify({'status': 'error', 'message': f'Stream {stream_name} does not exist.'}), 404
    handlers = [handler.__name__ for handler in stream.handlers]
    return jsonify({'status': 'success', 'stream': {'name': stream.name, 'handlers': handlers}})

@app.route('/list_streams', methods=['GET'])
def list_streams():
    streams = stream_manager.list_streams()
    return jsonify({'streams': [stream.name for stream in streams]})


### ---------- Agent 相关的 API 端点 ---------- ###
@app.route('/add_agent', methods=['POST'])
def add_agent():
    data = request.json
    agent_category = data.get('category')
    agent_name = data.get('name')
    llm_type = data.get('llm_type')
    subscribed_streams = data.get('subscribed_streams', [])
    if agent_store.get_agent(agent_name):
        return jsonify({'status': 'error', 'message': f'Agent {agent_name} already exists.'}), 400
    try:
        agent = agent_store.create_agent(name=agent_name, category=agent_category, llm_type=llm_type)
        for stream_name in subscribed_streams:
            stream = stream_manager.get_stream(stream_name)
            if stream:
                agent.subscribe(stream)
        return jsonify({'status': 'success', 'agent': agent.name})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

#  添加自定义Agent
@app.route('/add_custom_agent', methods=['POST'])
def add_custom_agent():
    data = request.json
    agent_name = data.get('name')
    llm_type = data.get('llm_type')
    subscribed_streams = data.get('subscribed_streams', [])
    prompt = data.get('prompt', '')

    if not agent_name or not llm_type or not prompt:
        return jsonify({'status': 'error', 'message': 'Agent name, LLM API key, and prompt are required.'}), 400

    try:
        # 定义一个UserDefinedAgent类继承自BuiltInAgent
        class UserDefinedAgent(PromptAgent):
            def generate_prompt(self, data: Any) -> str:
                return prompt + " " + str(data)

        agent = UserDefinedAgent(name=agent_name, llm_type=llm_type, socketio=socketio)
        agent_store.add_agent(agent)
        for stream_name in subscribed_streams:
            stream = stream_manager.get_stream(stream_name)
            if stream:
                agent.subscribe(stream)
        return jsonify({'status': 'success', 'agent': agent.name})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/delete_agent', methods=['POST'])
def delete_agent():
    data = request.json
    agent_name = data.get('name')
    if not agent_name:
        return jsonify({'status': 'error', 'message': 'Agent name is required.'}), 400
    agent_store.remove_agent(agent_name)
    return jsonify({'status': 'success', 'message': f'Agent {agent_name} deleted.'})

@app.route('/get_agent', methods=['GET'])
def get_agent():
    agent_name = request.args.get('name')
    if not agent_name:
        return jsonify({'status': 'error', 'message': 'Agent name is required.'}), 400
    agent = agent_store.get_agent(agent_name)
    if not agent:
        return jsonify({'status': 'error', 'message': f'Agent {agent_name} does not exist.'}), 404
    # import pdb; pdb.set_trace()
    agent_handler_name = f"agent_handler_{agent.name}"
    subscribed_streams = [stream.name for stream in stream_manager.list_streams() if any(agent_handler_name in handler.__name__ for handler in stream.handlers)]
    return jsonify({'status': 'success', 'agent': {'name': agent.name, 'llm_type': agent.llm_type, 'subscribed_streams': subscribed_streams}})

@app.route('/get_built_in_agents', methods=['GET'])
def get_built_in_agents():
    # 假设内置Agents已经在config.yaml中定义
    built_in_agents = [agent.name for agent in agent_store.get_builtin_agents()]
    return jsonify({'agents': built_in_agents})

@app.route('/list_agents', methods=['GET'])
def list_agents():
    agents = agent_store.list_agents()
    return jsonify({'agents': [agent.name for agent in agents]})

@app.route('/list_agent_categories', methods=['GET'])
def list_agent_categories():
    agent_categories = agent_store.list_agent_categories()
    return jsonify({'agent_categories': agent_categories})


### ---------- Subscribe 相关的 API 端点 ---------- ###
# subscribe_stream
@app.route('/subscribe_stream', methods=['POST'])
def subscribe_stream():
    data = request.json
    stream_name = data.get('stream')
    agent_name = data.get('agent')
    if not stream_name or not agent_name:
        return jsonify({'status': 'error', 'message': 'Stream name and agent name are required.'}), 400
    stream = stream_manager.get_stream(stream_name)
    agent = agent_store.get_agent(agent_name)
    if not stream or not agent:
        return jsonify({'status': 'error', 'message': 'Stream or agent does not exist.'}), 404
    agent.subscribe(stream)
    return jsonify({'status': 'success', 'message': f'Agent {agent_name} subscribed to stream {stream_name}.'})


### ---------- Emit 相关的 API 端点 ---------- ###
@app.route('/emit_data', methods=['POST'])
def emit_data():
    data = request.json
    stream_name = data.get('stream')
    payload = data.get('data')
    if not stream_name or payload is None:
        return jsonify({'status': 'error', 'message': 'Stream name and data are required.'}), 400
    stream = stream_manager.get_stream(stream_name)
    if not stream:
        return jsonify({'status': 'error', 'message': f'Stream {stream_name} does not exist.'}), 400
    # 在独立线程中发射数据，避免阻塞Flask
    threading.Thread(target=stream.emit, args=(payload,)).start()
    return jsonify({'status': 'success', 'message': f'Data emitted to stream {stream_name}.'})

### ---------- Config 相关的 API 端点 ---------- ###
# 从配置文件加载Graph
@app.route('/load_graph', methods=['GET'])
def load_graph():
    nodes, links = dsl_parser.parse()
    # print(nodes)
    # print(links)
    # nodes_name = [node.name for node in nodes]
    # links_name = [(link[0].name, link[1].name) for link in links]
    return jsonify({'status': 'success', 'nodes': nodes, 'links': links})

# 更新配置
@app.route('/update_config', methods=['POST'])
def update_config():
    data = request.json
    new_config = data.get('config')
    dsl_parser.update_config(new_config)
    config = dsl_parser.get_config()
    return jsonify({'status': 'success', 'config': config})


# SocketIO事件
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# 运行Flask应用
if __name__ == "__main__":
    # 使用eventlet作为异步模式
    socketio.run(app, host='0.0.0.0', port=12345)