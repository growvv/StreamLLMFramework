import os
from openai import OpenAI

# 方法 1：使用环境变量
api_key = os.getenv("OPENAI_API_KEY")

# 方法 2：直接在代码中设置（不推荐）

client = OpenAI(api_key=api_key)

def chat_with_gpt(prompt):
    try:
        response = client.chat.completions.create(model="gpt-4",   # 您可以根据需要选择模型，如 "gpt-3.5-turbo" 
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,       # 控制生成文本的长度
        temperature=0.7,      # 控制生成文本的创造性
        n=1,                  # 生成的回答数量
        stop=None             # 设置停止生成的标识
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    user_input = "请介绍一下 Python 的装饰器。"
    gpt_response = chat_with_gpt(user_input)
    print("GPT-4 回复:", gpt_response)
