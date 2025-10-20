from flask import Flask, render_template, request, jsonify, session
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional

# LangChain imports
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# Langfuse import
from langfuse.langchain import CallbackHandler as LangfuseCallbackHandler

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# API配置
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

# LangSmith 配置（可选 - 用于监控和调试）
# 通过环境变量启用：
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=your_api_key
# LANGCHAIN_PROJECT=your_project_name
LANGSMITH_ENABLED = os.getenv('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'

# Langfuse 配置（可选 - 用于 LLM 应用可观测性）
LANGFUSE_ENABLED = os.getenv('LANGFUSE_ENABLED', 'false').lower() == 'true'
langfuse_handler = None

if LANGFUSE_ENABLED:
    try:
        # CallbackHandler automatically reads from environment variables:
        # LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST
        langfuse_handler = LangfuseCallbackHandler()
    except Exception as e:
        print(f"⚠️  Langfuse 初始化失败: {e}")
        LANGFUSE_ENABLED = False

# 初始化 LangChain ChatAnthropic
llm = None
if ANTHROPIC_API_KEY:
    llm = ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        anthropic_api_key=ANTHROPIC_API_KEY,
        max_tokens=1024
    )

# 使用 @tool 装饰器定义天气工具
@tool
def get_weather(city: str, units: str = "metric") -> dict:
    """获取指定城市的当前天气信息。支持中文和英文城市名称。

    Args:
        city: 城市名称，例如：北京、上海、New York、London
        units: 温度单位，metric (摄氏度) 或 imperial (华氏度)，默认为 metric

    Returns:
        包含天气信息的字典，包括温度、湿度、天气描述等
    """
    if not OPENWEATHERMAP_API_KEY:
        return {"error": "未配置OpenWeatherMap API密钥"}

    try:
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": OPENWEATHERMAP_API_KEY,
            "units": units,
            "lang": "zh_cn"
        }

        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # 格式化天气信息
        weather_info = {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "units": "°C" if units == "metric" else "°F"
        }

        return weather_info

    except requests.exceptions.RequestException as e:
        return {"error": f"无法获取天气信息：{str(e)}"}
    except KeyError as e:
        return {"error": f"天气数据格式错误：{str(e)}"}

# 将工具绑定到 LLM
if llm:
    llm_with_tools = llm.bind_tools([get_weather])

def convert_to_langchain_messages(messages_dict_list):
    """将 Flask session 中的字典消息转换为 LangChain 消息对象"""
    langchain_messages = []

    for msg in messages_dict_list:
        role = msg.get("role")
        content = msg.get("content")

        if role == "user":
            langchain_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            langchain_messages.append(AIMessage(content=content))

    return langchain_messages

@app.route('/')
def index():
    """聊天页面"""
    # 初始化会话历史
    if 'messages' not in session:
        session['messages'] = []
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    if not llm:
        return jsonify({
            'error': '未配置Anthropic API密钥，请在.env文件中设置ANTHROPIC_API_KEY'
        }), 500

    try:
        data = request.json
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': '消息不能为空'}), 400

        # 获取或初始化会话历史
        if 'messages' not in session:
            session['messages'] = []

        # 添加用户消息到历史
        messages = session['messages']
        messages.append({
            "role": "user",
            "content": user_message
        })

        # 转换为 LangChain 消息格式
        langchain_messages = convert_to_langchain_messages(messages)

        # 准备 callbacks
        callbacks = []
        if langfuse_handler:
            callbacks.append(langfuse_handler)

        # 调用 LangChain (带工具)
        response = llm_with_tools.invoke(langchain_messages, config={"callbacks": callbacks})

        # 处理工具调用
        while response.tool_calls:
            # 执行所有工具调用
            tool_messages = []
            for tool_call in response.tool_calls:
                # 调用工具函数
                tool_result = get_weather.invoke(tool_call["args"])

                # 创建工具消息
                tool_msg = ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"]
                )
                tool_messages.append(tool_msg)

            # 将响应和工具结果添加到消息历史
            langchain_messages.append(response)
            langchain_messages.extend(tool_messages)

            # 继续对话
            response = llm_with_tools.invoke(langchain_messages, config={"callbacks": callbacks})

        # 提取最终文本响应
        assistant_message = response.content

        # 将助手最终响应添加到历史
        messages.append({
            "role": "assistant",
            "content": assistant_message
        })

        # 限制历史长度（保留最近10轮对话）
        if len(messages) > 20:
            messages = messages[-20:]

        session['messages'] = messages
        session.modified = True

        return jsonify({
            'response': assistant_message,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': f'服务器错误：{str(e)}'}), 500

@app.route('/clear', methods=['POST'])
def clear_history():
    """清除对话历史"""
    session['messages'] = []
    session.modified = True
    return jsonify({'success': True})

if __name__ == '__main__':
    # 生产环境配置
    PORT = int(os.getenv('PORT', 8080))
    DEBUG = os.getenv('FLASK_ENV') != 'production'

    print("\n" + "="*60)
    print("🤖 AI聊天应用 (LangChain版本 - 支持天气查询)")
    print("="*60)

    if not ANTHROPIC_API_KEY:
        print("⚠️  警告：未找到ANTHROPIC_API_KEY")
        print("   请复制.env.example为.env并设置你的API密钥")

    if not OPENWEATHERMAP_API_KEY:
        print("⚠️  警告：未找到OPENWEATHERMAP_API_KEY")
        print("   天气查询功能将不可用")

    # LangSmith 状态
    if LANGSMITH_ENABLED:
        project_name = os.getenv('LANGCHAIN_PROJECT', 'default')
        print(f"\n✓ LangSmith 监控已启用")
        print(f"  项目名称: {project_name}")
        print(f"  查看追踪: https://smith.langchain.com/")
    else:
        print("\n💡 提示：可以启用 LangSmith 监控 LLM 和工具调用")
        print("   在 .env 中设置: LANGCHAIN_TRACING_V2=true")

    # Langfuse 状态
    if LANGFUSE_ENABLED:
        langfuse_host = os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')
        print(f"\n✓ Langfuse 监控已启用")
        print(f"  查看追踪: {langfuse_host}")
    else:
        print("\n💡 提示：可以启用 Langfuse 监控 LLM 和工具调用")
        print("   在 .env 中设置: LANGFUSE_ENABLED=true")

    if DEBUG:
        print(f"\n访问地址：http://localhost:{PORT}")
    else:
        print(f"\n🚀 生产模式运行在端口 {PORT}")
    print("="*60 + "\n")

    # 在生产环境中使用 0.0.0.0，开发环境使用 localhost
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
