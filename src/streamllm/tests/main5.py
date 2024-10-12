from streamllm.framework.dsl_parser import DSLParser

# 使用框架
if __name__ == "__main__":
    # 初始化 DSLParser，假设配置文件为 config.yaml
    parser = DSLParser(config_path="config5.yaml")
    parser.parse()

    parser.update_config({
        "streams": [
            {
                "name": "text_streamaaaa",
                "handlers": [
                    {"type": "text_handler"},
                    {"type": "agent_handler"},
                    {"type": "forwarding_handler", "target": "analytics_stream"}
                ]
            }
        ]
    })
    parser.update_config({'streams': [{'name': 'text_stream222', 'handlers': [{"type": "text_handler"}]}]})

    name = "TextAgent"
    category = "AssistAgent"
    llm_type = "qwen"
    analytics_stream = ["analytics_stream"]
    # TextAgent = agent_store.create_agent(name=name, category=category)
    agent_config_dict = {
        "name": name,
        "category": category,
        "llm_type": llm_type,
        "subscribed_streams": analytics_stream
    }
    parser.update_config({
        "agents": [agent_config_dict]
    })


    print(parser.get_config())
