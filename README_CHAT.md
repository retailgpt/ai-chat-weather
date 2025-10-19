# AI聊天应用 - 支持天气查询（MCP）

这是一个基于Flask和Claude AI的聊天应用，支持通过MCP（Model Context Protocol）模式调用天气API。

## 功能特点

- 🤖 **AI对话**：使用Claude AI进行自然语言对话
- 🌤️ **天气查询**：自动识别天气相关问题并调用OpenWeatherMap API
- 🔧 **MCP工具调用**：Claude自动判断何时需要使用天气工具
- 💬 **会话管理**：支持上下文对话，保留对话历史
- 🎨 **现代化UI**：美观的聊天界面，支持实时消息显示

## 安装步骤

### 1. 安装依赖

所需的包已经安装：
```bash
pip3 install flask anthropic requests python-dotenv
```

### 2. 配置API密钥

复制 `.env.example` 为 `.env` 并填入你的API密钥：

```bash
cp .env.example .env
```

然后编辑 `.env` 文件：

```env
ANTHROPIC_API_KEY=你的Claude_API密钥
OPENWEATHERMAP_API_KEY=你的天气API密钥
```

#### 获取API密钥

- **Claude API密钥**：访问 https://console.anthropic.com/ 注册并获取
- **OpenWeatherMap API密钥**：访问 https://openweathermap.org/api 注册免费账户

### 3. 运行应用

```bash
python3 chat_app.py
```

应用将在 http://localhost:8080 启动

## 使用示例

### 天气查询示例

- "北京今天天气怎么样？"
- "上海现在的温度是多少？"
- "What's the weather like in New York?"
- "伦敦的天气如何？"

### 普通对话示例

- "给我讲个笑话"
- "什么是量子计算？"
- "帮我写一首诗"
- "Python和JavaScript有什么区别？"

## 技术架构

### 后端 (chat_app.py)

- **Flask框架**：提供Web服务
- **Anthropic SDK**：集成Claude API
- **Tool Use (MCP)**：定义天气工具，Claude自动判断何时调用
- **会话管理**：使用Flask session保存对话历史

### 天气工具定义

```python
weather_tool = {
    "name": "get_weather",
    "description": "获取指定城市的当前天气信息",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string"},
            "units": {"type": "string", "enum": ["metric", "imperial"]}
        }
    }
}
```

### 前端 (chat.html)

- 响应式聊天界面
- 实时消息显示
- 输入中状态指示
- 错误处理和提示

## MCP工作原理

1. 用户提问："北京天气怎么样？"
2. Claude识别这是天气查询，调用 `get_weather` 工具
3. 后端执行 `get_weather("北京")` 调用OpenWeatherMap API
4. 将天气数据返回给Claude
5. Claude基于天气数据生成自然语言回答
6. 用户看到："北京目前温度15°C，多云..."

## 文件结构

```
claude_codes/
├── chat_app.py          # Flask应用主文件
├── templates/
│   └── chat.html        # 聊天界面
├── .env.example         # API密钥模板
├── .env                 # 你的API密钥（不要提交到git）
└── README_CHAT.md       # 本文件
```

## 注意事项

1. **API配额**：注意Claude和OpenWeatherMap的API使用配额
2. **安全性**：不要将 `.env` 文件提交到版本控制系统
3. **会话限制**：对话历史限制在最近20条消息，避免超出token限制
4. **错误处理**：应用包含基本错误处理，但生产环境需要更完善的处理

## 故障排查

### 问题：提示"未配置API密钥"
**解决**：检查 `.env` 文件是否存在且包含正确的API密钥

### 问题：天气查询不工作
**解决**：
1. 检查OPENWEATHERMAP_API_KEY是否正确
2. 确认OpenWeatherMap账户已激活（新注册需要等待几分钟）
3. 检查城市名称拼写

### 问题：Claude响应很慢
**解决**：这是正常的，Claude API需要时间处理请求，尤其是使用工具时

## 扩展建议

- 添加更多工具（股票查询、新闻搜索等）
- 实现用户认证系统
- 添加对话历史持久化（数据库）
- 支持流式响应（SSE）
- 添加语音输入/输出

## 许可

本项目仅供学习和演示使用。
