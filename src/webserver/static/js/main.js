var socket = io();

// 数据结构
var nodes = [];
var links = [];

// D3.js 初始化
var width = document.getElementById('graph').clientWidth;
var height = document.getElementById('graph').clientHeight;

var svg = d3.select("#graph").append("svg")
    .attr("width", width)
    .attr("height", height);

var simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(200))
    .force("charge", d3.forceManyBody().strength(-500))
    .force("center", d3.forceCenter(width / 2, height / 2));

var link = svg.append("g")
    .attr("stroke", "#999")
    .attr("stroke-opacity", 0.6)
    .selectAll("line")
    .data(links)
    .enter().append("line")
    .attr("stroke-width", 2);

var node = svg.append("g")
    .attr("stroke", "#fff")
    .attr("stroke-width", 1.5)
    .selectAll("circle")
    .data(nodes)
    .enter().append("circle")
    .attr("r", 20)
    .attr("fill", "#69b3a2")
    .call(drag(simulation));

var label = svg.append("g")
    .selectAll("text")
    .data(nodes)
    .enter().append("text")
    .attr("dy", -25)
    .attr("text-anchor", "middle")
    .text(d => d.id);

simulation.on("tick", () => {
    link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

    label
        .attr("x", d => d.x)
        .attr("y", d => d.y);
});

function drag(simulation) {
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
}

// 添加Stream到图表
function addStreamToGraph(streamName) {
    if (!nodes.find(n => n.id === streamName)) {
        nodes.push({id: streamName, type: 'stream'});
        updateGraph();
    }
}

// 添加Agent到图表
function addAgentToGraph(agentName) {
    if (!nodes.find(n => n.id === agentName)) {
        nodes.push({id: agentName, type: 'agent'});
        updateGraph();
    }
}

// 添加连接线到图表
function addLinkToGraph(source, target) {
    if (!links.find(l => l.source === source && l.target === target)) {
        links.push({source, target});
        updateGraph();
    }
}

// 更新图表
function updateGraph() {
    link = link.data(links);
    link.exit().remove();
    link = link.enter().append("line")
        .attr("stroke-width", 2)
        .merge(link);

    node = node.data(nodes);
    node.exit().remove();
    node = node.enter().append("circle")
        .attr("r", 20)
        .attr("fill", d => d.type === 'stream' ? '#69b3a2' : '#ff7f0e')
        .call(drag(simulation))
        .merge(node);

    label = label.data(nodes);
    label.exit().remove();
    label = label.enter().append("text")
        .attr("dy", -25)
        .attr("text-anchor", "middle")
        .text(d => d.id)
        .merge(label);

    simulation.nodes(nodes);
    simulation.force("link").links(links);
    simulation.alpha(1).restart();
}

// SocketIO事件处理
socket.on('data_flow', function(msg) {
    console.log('Data Flow:', msg);
    // 根据事件更新图表或显示数据流动
    // 示例：高亮相关节点或添加动态链接
    // 例如，高亮发射和转发的数据流
    if(msg.action === 'emit') {
        highlightStream(msg.stream);
    } else if(msg.action === 'forward') {
        highlightLink(msg.stream, msg.target_stream);
    }
});

function highlightStream(streamName) {
    node.filter(d => d.id === streamName)
        .classed('highlight', true)
        .transition()
        .duration(3000)
        .attr('stroke', 'yellow')
        .attr('stroke-width', 5)
        .transition()
        .duration(1000)
        .attr('stroke', '#fff')
        .attr('stroke-width', 1.5)
        .classed('highlight', false);
}

function highlightLink(source, target) {
    link.filter(d => d.source.id === source && d.target.id === target)
        .attr('stroke', 'red')
        .attr('stroke-width', 5)
        .transition()
        .duration(3000)
        .attr('stroke', '#999')
        .attr('stroke-width', 2);
}

function highlightAgent(agentName) {
    node.filter(d => d.id === agentName)
        .classed('highlight', true)
        .transition()
        .duration(3000)
        .attr('stroke', 'yellow')
        .attr('stroke-width', 5)
        .transition()
        .duration(1000)
        .attr('stroke', '#fff')
        .attr('stroke-width', 1.5)
        .classed('highlight', false);
}

socket.on('agent_response', function(msg) {
    console.log('Agent Response:', msg);
    // 在UI中显示Agent的响应
    // alert(`Agent ${msg.agent} 响应: ${msg.response}`);
    highlightAgent(msg.agent);
});

// 加载All Agents
function loadAgents() {
    fetch('/list_agents')
        .then(response => response.json())
        .then(data => {
            var select = document.getElementById('subscribe_agent_select');
            select.innerHTML = '';
            data.agents.forEach(agent => {
                var option = document.createElement('option');
                option.value = agent;
                option.text = agent;
                select.appendChild(option);
            });
        });
}

// 加载Agent种类
function loadAgentCategories() {
    fetch('/list_agent_categories')
        .then(response => response.json())
        .then(data => {
            var select = document.getElementById('create_agent_select');
            select.innerHTML = '';
            data.agent_categories.forEach(category => {
                var option = document.createElement('option');
                option.value = category;
                option.text = category;
                select.appendChild(option);
            });
        });
}

// 加载All Streams
function loadStreams() {
    fetch('/list_streams')
        .then(response => response.json())
        .then(data => {
            var selectForSubscribe = document.getElementById('subscribe_stream_select');
            selectForSubscribe.innerHTML = '';
            data.streams.forEach(stream => {
                var option = document.createElement('option');
                option.value = stream;
                option.text = stream;
                selectForSubscribe.appendChild(option);
            });

            var selectForAgent = document.getElementById('emit_stream_select');
            selectForAgent.innerHTML = '';
            data.streams.forEach(stream => {
                var option = document.createElement('option');
                option.value = stream;
                option.text = stream;
                selectForAgent.appendChild(option);
            });
        });
}

// 从配置文件加载Graph
function loadGraph() {
    fetch('/load_graph')
    .then(response => response.json())
    .then(data => {
        nodes = data.nodes;  // ('text_stream', 'analytics_stream')
        links = data.links;  // ('text_stream', 'analytics_stream'),
        updateGraph();
    });
}

// 添加Stream函数
function addStream() {
    var streamName = document.getElementById('stream_name').value.trim();
    if (!streamName) {
        alert('Stream名称不能为空');
        return;
    }
    fetch('/add_stream', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name: streamName})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            addStreamToGraph(streamName);
            // 更新Agent的Stream选项
            loadStreams();
            updateConfigForStream(streamName);
            alert(`Stream ${streamName} 添加成功`);
        } else {
            alert(`错误: ${data.message}`);
        }
    });
}

// 添加 Agent函数
function addAgent() {
    var agentCategory = document.getElementById('create_agent_select').value;
    if (!agentCategory) {
        alert('请选择一个内置 Agent');
        return;
    }
    var agentName = document.getElementById('create_agents_name').value;
    if (!agentName) {
        alert('请给Agent命名')
        return;
    }
    var llm_type = document.getElementById('create_agents_llm_type').value;
    // if (!llm_type) {
    //     alert('请给指定LLM类型')
    //     return;
    // }
    fetch('/add_agent', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            category: agentCategory,
            name: agentName,  // 可通过界面输入或预设
            llm_type: llm_type, 
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            addAgentToGraph(agentName);
            loadAgents();
            updateConfigForAgent(agentName, agentCategory, llm_type);
            alert(`内置 Agent ${agentName} 添加成功`);
        } else {
            alert(`错误: ${data.message}`);
        }
    });
}

// 订阅函数
function subscribeStreamToAgent() {
    var agentName = document.getElementById('subscribe_agent_select').value.trim();
    var streamName = document.getElementById('subscribe_stream_select').value.trim();

    if (!agentName || !streamName) {
        alert('Agent和Stream不能为空');
        return;
    }

    fetch('/subscribe_stream', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            agent: agentName,
            stream: streamName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            addLinkToGraph(agentName, streamName);
            updateConfigForSubscribe(agentName, streamName);
            // alert(`Agent ${agentName} 订阅了Stream ${streamName}`);
        } else {
            alert(`错误: ${data.message}`);
        }
    });
}

// 发射数据函数
function emitData() {
    var streamName = document.getElementById('emit_stream_select').value.trim();
    var data = document.getElementById('emit_data').value.trim();

    if (!streamName || !data) {
        alert('Stream名称和数据不能为空');
        return;
    }

    fetch('/emit_data', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            stream: streamName,
            data: data
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // alert(`数据已发射到Stream ${streamName}`);
        } else {
            alert(`错误: ${data.message}`);
        }
    });
}

// update_config_for_stream
function updateConfigForStream(streamName, handlers = []) {
    stream_dict = {
        "streams": [
            {
                "name": streamName,
                "handlers": handlers
            }
        ]
    }
    fetch('/update_config', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({config: stream_dict})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // alert(`Stream ${streamName} 配置更新成功`);
        } else {
            alert(`错误: ${data.message}`);
        }
    });
}

// update_config_for_agent
function updateConfigForAgent(agentName, category, llm_type) {
    agent_dict = {
        "agents": [
            {
                "name": agentName,
                "category": category,
                "llm_type": llm_type,
                "subscribed_streams": []
            }
        ]
    }
    fetch('/update_config', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({config: agent_dict})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // alert(`Agent ${agentName} 配置更新成功`);
        } else {
            alert(`错误: ${data.message}`);
        }
    });
}

// updateConfigForSubscribe
function updateConfigForSubscribe(agentName, streamName) {
    agent_dict = {
        "agent_subscriptions": [
            {
                "name": agentName,
                "subscribed_streams": [streamName]
            }
        ]
    }
    fetch('/update_config', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({config: agent_dict})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // alert(`Agent ${agentName} 订阅Stream ${streamName} 配置更新成功`);
        } else {
            alert(`错误: ${data.message}`);
        }
    });
}

// 初始化加载内置Agents和Streams
window.onload = function() {
    loadAgents();
    loadStreams();
};

document.addEventListener('DOMContentLoaded', function() {
    loadAgentCategories();
    loadAgents();
    loadStreams();
    loadGraph();
});