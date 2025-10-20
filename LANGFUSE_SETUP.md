# Langfuse 集成指南

Langfuse 是一个开源的 LLM 应用可观测性平台，可以追踪和分析您的 AI 应用性能。

## 🚀 快速开始

### 步骤 1: 注册 Langfuse 账号

1. 访问 https://cloud.langfuse.com/
2. 点击 "Sign Up" 注册账号
3. 可以使用 GitHub、Google 或邮箱注册

### 步骤 2: 创建项目并获取 API 密钥

1. **登录后**，如果是新账号会提示创建项目
2. **项目名称**: `ai-chat-weather` (或您喜欢的名称)
3. **获取 API 密钥**:
   - 点击左侧菜单 "Settings" → "API Keys"
   - 或直接访问: https://cloud.langfuse.com/project/settings
   - 点击 "Create new API keys"
   - 会生成两个密钥：
     - `Public Key` (pk-xxx...)
     - `Secret Key` (sk-xxx...)
   - **⚠️ 复制并保存这两个密钥！Secret Key 只显示一次！**

### 步骤 3: 配置本地环境

编辑 `.env` 文件，添加以下内容：

```env
# Langfuse 配置
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

**替换为您的实际密钥**！

### 步骤 4: 本地测试

```bash
# 停止之前的服务器
# 启动应用
python3 chat_app_langchain.py
```

您应该看到：
```
✓ Langfuse 监控已启用
  查看追踪: https://cloud.langfuse.com
```

### 步骤 5: 测试追踪

1. 打开浏览器访问 http://localhost:8080
2. 发送一条消息，例如：
   - "北京今天天气怎么样？"
   - "给我讲个笑话"
3. 访问 Langfuse Dashboard: https://cloud.langfuse.com/
4. 在 "Traces" 页面应该能看到刚才的对话记录

## 📊 Langfuse 功能介绍

### Traces（追踪）
查看每次对话的完整链路：
- LLM 输入和输出
- Token 使用量
- 延迟时间
- 工具调用详情

### Sessions（会话）
追踪用户的完整对话会话

### Metrics（指标）
- Token 使用统计
- 成本分析
- 错误率监控
- 延迟分析

### Playground
测试和优化您的 prompts

### Datasets
创建测试数据集用于评估

## 🆚 Langfuse vs LangSmith

| 特性 | Langfuse | LangSmith |
|------|----------|-----------|
| **开源** | ✅ 是 | ❌ 否 |
| **价格** | 免费套餐慷慨 | 免费套餐有限 |
| **自托管** | ✅ 支持 | ❌ 不支持 |
| **界面** | 现代化 | 功能丰富 |
| **集成** | LangChain 原生支持 | LangChain 官方 |

**可以同时使用两者！**

## 🔄 同时使用 LangSmith 和 Langfuse

您可以同时启用两个监控平台：

```env
# LangSmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_...
LANGCHAIN_PROJECT=ai-chat-weather

# Langfuse
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

两个平台会同时记录所有追踪数据！

## 🚀 部署到 Render

### 添加环境变量

在 Render Dashboard 中：
1. 进入您的服务 `ai-chat-weather`
2. 点击 "Environment" 标签
3. 添加以下环境变量：

```
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

4. 点击 "Save Changes"
5. Render 会自动重新部署

### 推送代码

```bash
git add .
git commit -m "Add Langfuse monitoring"
git push
```

Render 会自动部署更新！

## 📖 高级功能

### 1. 自定义追踪名称

可以通过设置 session_id 来组织追踪：

```python
langfuse_handler = CallbackHandler(
    session_id="user-123",  # 按用户组织
    user_id="user-123",
    # ...
)
```

### 2. 添加标签

为追踪添加标签便于筛选：

```python
langfuse_handler = CallbackHandler(
    tags=["production", "weather-query"],
    # ...
)
```

### 3. 评分和反馈

通过 Langfuse API 可以添加用户反馈评分

### 4. 提示管理

在 Langfuse 中管理和版本控制您的 prompts

## 🔍 故障排查

### 问题：未看到追踪数据

**检查**:
1. 确认 `.env` 文件中 `LANGFUSE_ENABLED=true`
2. 确认 API 密钥正确
3. 检查应用启动时是否显示 "✓ Langfuse 监控已启用"
4. 查看控制台是否有错误信息

### 问题：API 密钥错误

**解决**:
1. 重新访问 https://cloud.langfuse.com/project/settings
2. 确认复制了正确的密钥
3. 注意 Public Key 和 Secret Key 不要搞混

### 问题：追踪数据延迟

**说明**: Langfuse 有轻微延迟（通常几秒钟），刷新页面即可看到新数据

## 🎓 学习资源

- **官方文档**: https://langfuse.com/docs
- **LangChain 集成**: https://langfuse.com/docs/integrations/langchain
- **GitHub**: https://github.com/langfuse/langfuse
- **Discord 社区**: https://langfuse.com/discord

## 💡 提示

1. **开发环境**: 本地测试时启用 Langfuse 便于调试
2. **生产环境**: 部署后也启用，监控实际用户使用情况
3. **数据保留**: 免费套餐通常保留 30 天数据
4. **自托管**: 如果有隐私需求，可以自托管 Langfuse

祝您使用愉快！🎉
