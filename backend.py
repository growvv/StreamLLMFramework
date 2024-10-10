import eventlet
# 使用 eventlet 作为异步模式
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading

from dsl_parser import DSLParser
from stream_manager import StreamManager
from agent_store import AgentStore
from agent import Agent
from handler import agent_handler_factory


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

# 定义Flask路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_stream', methods=['POST'])
def add_stream():
    data = request.json
    stream_name = data.get('name')
    if not stream_name:
        return jsonify({'status': 'error', 'message': 'Stream name is required.'}), 400
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

@app.route('/add_agent', methods=['POST'])
def add_agent():
    data = request.json
    agent_name = data.get('name')
    llm_type = data.get('llm_type')
    subscribed_streams = data.get('subscribed_streams', [])
    try:
        # agent = Agent(name=agent_name, llm_api_key=llm_api_key, socketio=socketio)
        agent = agent_store.create_agent(agent_name, llm_type)
        for stream_name in subscribed_streams:
            stream = stream_manager.get_stream(stream_name)
            if stream:
                handler = agent_handler_factory(agent)
                stream.register_handler(handler)
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
    return jsonify({'status': 'success', 'streams': [stream.name for stream in streams]})

@app.route('/list_agents', methods=['GET'])
def list_agents():
    agents = agent_store.list_agents()
    return jsonify({'status': 'success', 'agents': [agent.name for agent in agents]})

@app.route('/add_agent_handler', methods=['POST'])
def add_handler():
    data = request.json
    stream_name = data.get('stream')
    agent_name = data.get('agent')
    if not stream_name or not agent_name:
        return jsonify({'status': 'error', 'message': 'Stream name and agent name are required.'}), 400
    stream = stream_manager.get_stream(stream_name)
    agent = agent_store.get_agent(agent_name)
    if not stream or not agent:
        return jsonify({'status': 'error', 'message': 'Stream or agent does not exist.'}), 404
    handler = agent_handler_factory(agent)
    stream.register_handler(handler)
    return jsonify({'status': 'success', 'message': f'Handler added to stream {stream_name}.'})

@app.route('/add_normal_handler', methods=['POST'])
def add_normal_handler():
    data = request.json
    stream_name = data.get('stream')
    handler_name = data.get('handler')
    if not stream_name or not handler_name:
        return jsonify({'status': 'error', 'message': 'Stream name and handler name are required.'}), 400
    stream = stream_manager.get_stream(stream_name)
    if not stream:
        return jsonify({'status': 'error', 'message': 'Stream does not exist.'}), 404
    # Assuming handler_name corresponds to a callable handler function
    try:
        # import ipdb; ipdb.set_trace()
        
        print(handler_name)
        print(globals())
        handler = globals()[handler_name]
        stream.register_handler(handler)
        return jsonify({'status': 'success', 'message': f'Handler {handler_name} added to stream {stream_name}.'})
    except KeyError:
        return jsonify({'status': 'error', 'message': f'Handler {handler_name} does not exist.'}), 404


@app.route('/remove_handler', methods=['POST'])
def remove_handler():
    data = request.json
    stream_name = data.get('stream')
    handler_name = data.get('handler')
    if not stream_name or not handler_name:
        return jsonify({'status': 'error', 'message': 'Stream name and handler name are required.'}), 400
    stream = stream_manager.get_stream(stream_name)
    if not stream:
        return jsonify({'status': 'error', 'message': 'Stream does not exist.'}), 404
    handler = next((h for h in stream.handlers if h.__name__ == handler_name), None)
    if not handler:
        return jsonify({'status': 'error', 'message': 'Handler does not exist.'}), 404
    stream.unregister_handler(handler)
    return jsonify({'status': 'success', 'message': f'Handler {handler_name} removed from stream {stream_name}.'})

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
    socketio.run(app, host='0.0.0.0', port=5000)