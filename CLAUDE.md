# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains two Flask-based demonstration applications:

1. **TOTP Authentication App** (`app.py`) - Google Authenticator (TOTP) two-factor authentication demo
2. **AI Chat App** (`chat_app.py`) - Claude AI chatbot with MCP tool integration for weather queries

## Running the Applications

### TOTP Authentication App

```bash
# Install dependencies
pip3 install flask pyotp qrcode pillow

# Run the app
python3 app.py
```

Access at `http://localhost:5000`

### AI Chat App with Weather

**Original Version** (`chat_app.py`):
```bash
# Install dependencies
pip3 install flask anthropic requests python-dotenv

# Configure API keys (required)
cp .env.example .env
# Edit .env and add your API keys

# Run the app
python3 chat_app.py
```

**LangChain Version** (`chat_app_langchain.py`):
```bash
# Install dependencies
pip3 install flask langchain langchain-anthropic langchain-community requests python-dotenv

# Configure API keys (required)
cp .env.example .env
# Edit .env and add your API keys

# Run the app
python3 chat_app_langchain.py
```

Both versions access at `http://localhost:8080`

**Required API Keys** (configured in `.env`):
- `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com/
- `OPENWEATHERMAP_API_KEY` - Get from https://openweathermap.org/api

## Application Architecture

### TOTP Authentication App (`app.py`)

**Authentication Flow:**
1. `/setup` - User scans QR code or manually enters TOTP secret into Google Authenticator
2. `/` - User enters 6-digit code from authenticator app
3. `/verify` - Server validates TOTP code using `pyotp.TOTP.verify()` with `valid_window=1` (90-second tolerance)
4. Session management - Sets `session['authenticated'] = True` on success

**Key Implementation Details:**
- TOTP secret regenerates on each server restart (demo behavior)
- Flask session key regenerates on restart (`app.secret_key = os.urandom(24)`)
- QR code generated dynamically at `/qrcode` using `io.BytesIO()` for in-memory serving
- TOTP validation window of 1 accepts codes from previous/current/next 30-second windows

**Templates:**
- `login.html` - Login form with 6-digit code input
- `setup.html` - QR code display and manual setup instructions
- `welcome.html` - Protected page after authentication

### AI Chat App - Original Version (`chat_app.py`)

**MCP Tool Integration Architecture:**

The app implements Claude's tool use (MCP) pattern where Claude autonomously decides when to call external tools:

1. User asks question (e.g., "北京天气怎么样?")
2. Claude receives the `get_weather` tool definition in the API request
3. Claude returns `stop_reason="tool_use"` with tool call parameters
4. Backend executes `get_weather(city="北京")` → calls OpenWeatherMap API
5. Tool result sent back to Claude in a new message
6. Claude generates natural language response based on weather data

**Tool Definition Pattern:**

```python
weather_tool = {
    "name": "get_weather",
    "description": "获取指定城市的当前天气信息...",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string"},
            "units": {"type": "string", "enum": ["metric", "imperial"]}
        },
        "required": ["city"]
    }
}
```

**Session Management:**
- Conversation history stored in Flask session (`session['messages']`)
- History limited to most recent 20 messages to avoid token limits
- Messages include user input, assistant responses, tool use blocks, and tool results

**Tool Call Handling Loop:**

The app uses a `while response.stop_reason == "tool_use"` loop to handle multi-turn tool interactions:
- Extracts tool use blocks from Claude's response
- Calls `process_tool_call()` to execute the tool
- Appends assistant message (with tool_use content) to history
- Appends tool result as user message with `tool_result` type
- Continues conversation until Claude provides final text response

**API Integration:**
- Uses Anthropic SDK (`anthropic.Anthropic`) for Claude API
- Model: `claude-sonnet-4-5-20250929`
- Weather data from OpenWeatherMap REST API with Chinese language support (`lang=zh_cn`)

**Templates:**
- `chat.html` - Responsive chat interface with real-time messaging and typing indicators

### AI Chat App - LangChain Version (`chat_app_langchain.py`)

**LangChain Architecture:**

This version refactors the original app using LangChain, which provides higher-level abstractions for tool integration:

**Key Differences from Original:**

1. **LLM Initialization**: Uses `ChatAnthropic` from `langchain-anthropic` instead of raw `anthropic.Anthropic` client
   ```python
   llm = ChatAnthropic(
       model="claude-sonnet-4-5-20250929",
       anthropic_api_key=ANTHROPIC_API_KEY,
       max_tokens=1024
   )
   ```

2. **Tool Definition**: Uses `@tool` decorator instead of manual JSON schema
   ```python
   @tool
   def get_weather(city: str, units: str = "metric") -> dict:
       """获取指定城市的当前天气信息..."""
   ```
   - Type hints automatically generate input schema
   - Docstring becomes tool description
   - Cleaner, more Pythonic approach

3. **Tool Binding**: Uses `bind_tools()` to attach tools to LLM
   ```python
   llm_with_tools = llm.bind_tools([get_weather])
   ```

4. **Message Handling**: Uses LangChain message types (`HumanMessage`, `AIMessage`, `ToolMessage`)
   - Automatic conversion between Flask session dict format and LangChain objects
   - `ToolMessage` encapsulates tool results with `tool_call_id`

5. **Tool Call Loop**: Simplified with `while response.tool_calls:`
   - `response.tool_calls` returns structured tool call list
   - No manual parsing of response content blocks
   - Direct invocation: `get_weather.invoke(tool_call["args"])`
   - Automatic handling of multiple concurrent tool calls

**Advantages of LangChain Version:**
- Cleaner, more maintainable code (fewer lines)
- Type safety with Python type hints
- Easier to extend with additional tools
- Better integration with LangChain ecosystem (agents, chains, etc.)
- Automatic schema generation from function signatures

**Trade-offs:**
- Additional dependency (LangChain + sub-packages)
- Slight performance overhead from abstraction layer
- Need to understand both LangChain and Anthropic APIs

## Important Notes

### TOTP App
- **Server restarts** invalidate all sessions and require re-setup of authenticator apps
- **Production deployment** should use WSGI server (Gunicorn/uWSGI) instead of Flask dev server
- **Per-user secrets** should be stored in database, not single global `SECRET_KEY`

### AI Chat App
- **API quotas** - Monitor Claude and OpenWeatherMap usage limits
- **Security** - Never commit `.env` file to version control
- **Error handling** - Basic error handling included, production needs comprehensive handling
- **Tool extensibility** - Additional tools can be added to `tools=[]` array and handled in `process_tool_call()`

## File Structure

```
claude_codes/
├── app.py                   # TOTP authentication app
├── chat_app.py              # AI chat app with MCP tools (original)
├── chat_app_langchain.py    # AI chat app with LangChain
├── templates/
│   ├── login.html           # TOTP login form
│   ├── setup.html           # TOTP setup with QR code
│   ├── welcome.html         # TOTP protected page
│   └── chat.html            # AI chat interface
├── .env.example             # API key template
├── .env                     # Actual API keys (gitignored)
└── README_CHAT.md           # Chinese documentation for chat app
```
