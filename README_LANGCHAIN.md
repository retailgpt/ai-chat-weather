# AI聊天应用 - LangChain版本

这是使用 LangChain 框架重构的 AI 聊天应用，支持通过工具调用查询天气信息。

## 主要改进

与原始版本相比，LangChain 版本提供了：

- **更简洁的代码**: 使用 LangChain 的高级抽象，减少样板代码
- **类型安全**: 利用 Python 类型提示自动生成工具 schema
- **更易扩展**: 添加新工具只需定义函数并使用 `@tool` 装饰器
- **生态系统集成**: 可轻松集成 LangChain 的其他功能（agents、chains、memory 等）

## 快速开始

### 1. 安装依赖

```bash
pip3 install flask langchain langchain-anthropic langchain-community requests python-dotenv
```

### 2. 配置 API 密钥

```bash
cp .env.example .env
```

编辑 `.env` 文件，添加你的 API 密钥：

```env
ANTHROPIC_API_KEY=你的Claude_API密钥
OPENWEATHERMAP_API_KEY=你的天气API密钥
```

### 3. 运行应用

```bash
python3 chat_app_langchain.py
```

访问 http://localhost:8080

## 技术架构

### LangChain 核心组件

#### 1. ChatAnthropic - LLM 接口

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    anthropic_api_key=ANTHROPIC_API_KEY,
    max_tokens=1024
)
```

替代原始版本的 `anthropic.Anthropic()` client，提供统一的 LangChain 接口。

#### 2. @tool 装饰器 - 工具定义

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str, units: str = "metric") -> dict:
    """获取指定城市的当前天气信息。支持中文和英文城市名称。

    Args:
        city: 城市名称，例如：北京、上海、New York、London
        units: 温度单位，metric (摄氏度) 或 imperial (华氏度)

    Returns:
        包含天气信息的字典
    """
    # 实现代码...
```

**自动功能**:
- 从类型提示生成 input schema
- 从 docstring 提取工具描述和参数说明
- 无需手动编写 JSON schema

#### 3. bind_tools() - 工具绑定

```python
llm_with_tools = llm.bind_tools([get_weather])
```

将工具绑定到 LLM，Claude 会自动判断何时调用。

#### 4. Message Types - 消息类型

```python
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# 用户消息
HumanMessage(content="北京天气怎么样？")

# AI 响应
AIMessage(content="让我查询北京的天气...")

# 工具结果
ToolMessage(content=str(weather_data), tool_call_id="...")
```

提供类型安全的消息处理，替代原始版本的字典格式。

### 工具调用流程

```python
# 1. 调用 LLM
response = llm_with_tools.invoke(messages)

# 2. 检查是否需要调用工具
while response.tool_calls:
    # 3. 执行工具调用
    for tool_call in response.tool_calls:
        result = get_weather.invoke(tool_call["args"])

        # 4. 创建工具消息
        tool_msg = ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"]
        )
        messages.extend([response, tool_msg])

    # 5. 继续对话
    response = llm_with_tools.invoke(messages)

# 6. 返回最终响应
return response.content
```

### 与原始版本对比

| 特性 | 原始版本 | LangChain 版本 |
|------|---------|----------------|
| LLM 客户端 | `anthropic.Anthropic()` | `ChatAnthropic()` |
| 工具定义 | 手动 JSON schema | `@tool` 装饰器 |
| 消息格式 | 字典 | 类型化对象 |
| 工具调用检测 | `response.stop_reason == "tool_use"` | `response.tool_calls` |
| 工具执行 | 手动调用函数 | `tool.invoke()` |
| 代码行数 | ~237 行 | ~180 行 |

## 扩展示例

### 添加新工具

只需定义新函数并使用 `@tool` 装饰器：

```python
@tool
def search_news(query: str, limit: int = 5) -> list:
    """搜索最新新闻。

    Args:
        query: 搜索关键词
        limit: 返回结果数量，默认 5

    Returns:
        新闻列表
    """
    # 实现代码...
    pass

# 绑定多个工具
llm_with_tools = llm.bind_tools([get_weather, search_news])
```

### 使用 LangChain Agent

可以轻松升级为 Agent 模式：

```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(llm, [get_weather, search_news])
response = agent.invoke({"messages": [HumanMessage(content="北京天气如何？")]})
```

### 添加记忆功能

使用 LangChain 的 Memory 组件：

```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(return_messages=True)
```

## 使用示例

### 天气查询
- "北京今天天气怎么样？"
- "上海现在的温度是多少？"
- "What's the weather like in New York?"

### 普通对话
- "给我讲个笑话"
- "什么是量子计算？"
- "帮我写一首诗"

## 故障排查

### 问题：ModuleNotFoundError: No module named 'langchain'

**解决**: 确保安装了所有 LangChain 依赖

```bash
pip3 install langchain langchain-anthropic langchain-community
```

### 问题：pydantic 版本冲突

**解决**: LangChain 需要 pydantic v2，某些旧包可能需要 v1。可以忽略警告，或者更新冲突的包。

## LangSmith 监控

LangSmith 是 LangChain 官方的监控和调试平台，可以追踪每次 LLM 调用、工具执行和完整的对话链路。

### 启用 LangSmith

1. 在 https://smith.langchain.com/ 注册账户并获取 API key

2. 在 `.env` 文件中配置：

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_your_api_key_here
LANGCHAIN_PROJECT=ai-chat-weather
```

3. 重启应用，你会看到：

```
✓ LangSmith 监控已启用
  项目名称: ai-chat-weather
  查看追踪: https://smith.langchain.com/
```

### 查看追踪数据

访问 https://smith.langchain.com/，选择项目 `ai-chat-weather`，你可以看到：

- **LLM 调用详情**: 输入 prompt、输出内容、token 使用量、延迟
- **工具调用链路**: 哪些工具被调用、参数、返回值
- **错误追踪**: 如果有异常，完整的堆栈信息
- **性能分析**: 每个步骤的耗时、瓶颈分析

### 使用场景

- **调试工具调用**: 查看 Claude 为什么选择调用某个工具
- **优化 Prompt**: 对比不同 prompt 的效果
- **监控生产环境**: 追踪错误率、响应时间
- **成本分析**: 统计 token 使用量

## 资源链接

- [LangChain 文档](https://python.langchain.com/)
- [LangChain Anthropic 集成](https://python.langchain.com/docs/integrations/chat/anthropic)
- [工具使用指南](https://python.langchain.com/docs/modules/agents/tools/)
- [LangSmith 文档](https://docs.smith.langchain.com/)
- [Anthropic API](https://docs.anthropic.com/)
- [OpenWeatherMap API](https://openweathermap.org/api)

## 许可

本项目仅供学习和演示使用。
