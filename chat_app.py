from flask import Flask, render_template, request, jsonify, session
import anthropic
import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# API配置
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

# 初始化Anthropic客户端
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

# 定义天气工具
weather_tool = {
    "name": "get_weather",
    "description": "获取指定城市的当前天气信息。支持中文和英文城市名称。",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "城市名称，例如：北京、上海、New York、London"
            },
            "units": {
                "type": "string",
                "enum": ["metric", "imperial"],
                "description": "温度单位：metric (摄氏度) 或 imperial (华氏度)，默认为 metric",
                "default": "metric"
            }
        },
        "required": ["city"]
    }
}

def get_weather(city, units="metric"):
    """调用OpenWeatherMap API获取天气信息"""
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

def process_tool_call(tool_name, tool_input):
    """处理工具调用"""
    if tool_name == "get_weather":
        return get_weather(**tool_input)
    return {"error": f"未知工具：{tool_name}"}

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
    if not client:
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

        # 调用Claude API（带工具）
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            tools=[weather_tool],
            messages=messages
        )

        # 处理响应
        while response.stop_reason == "tool_use":
            # 找到工具使用块
            tool_use_block = None
            assistant_content = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_use_block = block
                # 转换为可序列化的字典格式
                if block.type == "text":
                    assistant_content.append({"type": "text", "text": block.text})
                elif block.type == "tool_use":
                    assistant_content.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })

            if not tool_use_block:
                break

            # 调用工具
            tool_result = process_tool_call(
                tool_use_block.name,
                tool_use_block.input
            )

            # 将助手响应添加到消息历史（已经是字典格式）
            messages.append({
                "role": "assistant",
                "content": assistant_content
            })

            # 添加工具结果
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_block.id,
                        "content": json.dumps(tool_result, ensure_ascii=False)
                    }
                ]
            })

            # 继续对话，让Claude使用工具结果
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                tools=[weather_tool],
                messages=messages
            )

        # 提取最终文本响应
        assistant_message = ""
        for block in response.content:
            if hasattr(block, "text"):
                assistant_message += block.text

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

    except anthropic.APIError as e:
        return jsonify({'error': f'Claude API错误：{str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'服务器错误：{str(e)}'}), 500

@app.route('/clear', methods=['POST'])
def clear_history():
    """清除对话历史"""
    session['messages'] = []
    session.modified = True
    return jsonify({'success': True})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🤖 AI聊天应用 (支持天气查询)")
    print("="*60)

    if not ANTHROPIC_API_KEY:
        print("⚠️  警告：未找到ANTHROPIC_API_KEY")
        print("   请复制.env.example为.env并设置你的API密钥")

    if not OPENWEATHERMAP_API_KEY:
        print("⚠️  警告：未找到OPENWEATHERMAP_API_KEY")
        print("   天气查询功能将不可用")

    print("\n访问地址：http://localhost:8080")
    print("="*60 + "\n")

    app.run(debug=True, port=8080)
