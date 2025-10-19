# 部署指南 - 使用 Render 平台

本指南将教您如何将 AI 聊天应用部署到 Render 平台，实现公网访问和一键更新。

## 为什么选择 Render？

- ✅ **完全免费**：免费套餐足够个人项目使用
- ✅ **GitHub 自动部署**：推送代码自动部署，实现一键更新
- ✅ **自动 HTTPS**：免费提供 SSL 证书
- ✅ **零配置**：支持 Python 应用开箱即用
- ✅ **环境变量管理**：安全存储 API 密钥

## 部署步骤

### 第一步：准备 GitHub 仓库

#### 1.1 初始化 Git 仓库（如果还没有）

```bash
cd /Users/jackzhan/claude_codes
git init
git add .
git commit -m "Initial commit: AI chat app with LangChain"
```

#### 1.2 在 GitHub 创建新仓库

1. 访问 https://github.com/new
2. 仓库名称：`ai-chat-weather`（或您喜欢的名称）
3. 设置为 **Private**（保护您的代码）
4. **不要**勾选 "Initialize this repository with a README"
5. 点击 "Create repository"

#### 1.3 推送代码到 GitHub

复制 GitHub 显示的命令，或执行以下命令：

```bash
# 添加远程仓库（替换为您的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/ai-chat-weather.git

# 推送代码
git branch -M main
git push -u origin main
```

### 第二步：在 Render 部署应用

#### 2.1 注册 Render 账号

1. 访问 https://render.com/
2. 点击 "Get Started" 或 "Sign Up"
3. 建议使用 GitHub 账号登录（方便后续操作）

#### 2.2 创建 Web Service

1. 登录后点击 "New +"
2. 选择 "Web Service"
3. 选择 "Connect a repository"
4. 如果是第一次使用，需要授权 Render 访问您的 GitHub
5. 找到并选择 `ai-chat-weather` 仓库
6. 点击 "Connect"

#### 2.3 配置部署设置

Render 会自动检测到 `render.yaml` 配置文件，但您也可以手动设置：

**基本配置**:
- **Name**: `ai-chat-weather`（服务名称，会成为 URL 的一部分）
- **Region**: 选择离您最近的区域（如 Singapore）
- **Branch**: `main`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn chat_app_langchain:app`

**实例类型**:
- 选择 **Free**（免费套餐）

#### 2.4 配置环境变量

这是最重要的一步！点击 "Advanced" 或在创建后进入 "Environment" 标签：

添加以下环境变量：

| Key | Value | 说明 |
|-----|-------|------|
| `ANTHROPIC_API_KEY` | `sk-ant-api03-...` | 您的 Claude API 密钥 |
| `OPENWEATHERMAP_API_KEY` | `fa51cd03de...` | 您的天气 API 密钥 |
| `LANGCHAIN_TRACING_V2` | `true` | 启用 LangSmith 监控 |
| `LANGCHAIN_API_KEY` | `lsv2_pt_...` | 您的 LangSmith API 密钥 |
| `LANGCHAIN_PROJECT` | `ai-chat-weather` | LangSmith 项目名称 |
| `FLASK_ENV` | `production` | 生产环境标识 |

**重要提示**：
- 从您的 `.env` 文件复制这些值
- **不要**将 `.env` 文件提交到 Git（已在 `.gitignore` 中排除）
- 环境变量的值不会显示在日志中，保护您的密钥安全

#### 2.5 创建和部署

1. 检查所有配置无误
2. 点击 "Create Web Service"
3. Render 开始自动部署（需要 3-5 分钟）

### 第三步：访问您的应用

部署完成后：

1. Render 会提供一个 URL，格式为：`https://ai-chat-weather-xxxx.onrender.com`
2. 点击 URL 或复制到浏览器访问
3. 开始使用您的 AI 聊天应用！

### 第四步：验证 LangSmith 监控

1. 访问 https://smith.langchain.com/
2. 登录您的账号
3. 选择项目 `ai-chat-weather`
4. 尝试在应用中发送消息
5. 在 LangSmith 中查看追踪数据

## 一键更新部署

这是 Render 的最大优势！

### 更新代码的步骤：

1. **本地修改代码**
   ```bash
   # 修改任何文件后
   git add .
   git commit -m "更新描述"
   ```

2. **推送到 GitHub**
   ```bash
   git push
   ```

3. **自动部署**
   - Render 会自动检测到代码变化
   - 自动重新构建和部署
   - 无需任何手动操作！
   - 通常 3-5 分钟完成

### 查看部署状态

- 在 Render Dashboard 中点击您的服务
- 查看 "Events" 标签页看到部署进度
- 查看 "Logs" 标签页看到应用日志

## 常见问题

### Q1: 免费套餐有什么限制？

**A**: Render 免费套餐限制：
- 750 小时/月运行时间（约 31 天，足够个人使用）
- 15 分钟无活动后自动休眠
- 首次访问时需要 30-60 秒唤醒
- 带宽和流量限制（通常足够）

💡 **提示**：可以使用 UptimeRobot 等服务定期 ping 您的应用，保持唤醒状态。

### Q2: 应用休眠后首次访问很慢？

**A**: 这是免费套餐的限制。解决方案：
- 升级到付费套餐（$7/月）获得始终在线
- 使用监控服务定期访问保持唤醒
- 接受首次加载较慢的现实

### Q3: 如何查看应用日志？

**A**:
1. 进入 Render Dashboard
2. 点击您的服务
3. 点击 "Logs" 标签
4. 可以看到实时日志和错误信息

### Q4: 如何更新环境变量？

**A**:
1. 进入 Render Dashboard
2. 点击您的服务
3. 点击 "Environment" 标签
4. 修改或添加环境变量
5. 点击 "Save Changes"
6. Render 会自动重启服务

### Q5: 部署失败了怎么办？

**A**: 检查以下几点：
1. 查看 "Logs" 中的错误信息
2. 确认 `requirements.txt` 中的包版本正确
3. 确认所有环境变量已正确配置
4. 确认 `render.yaml` 配置正确
5. 查看 Render 的 Build Logs

### Q6: 如何绑定自定义域名？

**A**:
1. 在 Render Dashboard 中点击服务
2. 进入 "Settings" > "Custom Domains"
3. 点击 "Add Custom Domain"
4. 按照指引配置 DNS（通常是添加 CNAME 记录）
5. Render 会自动配置 SSL 证书

## 成本考虑

### 免费套餐足够吗？

对于以下使用场景，**免费套餐完全足够**：
- ✅ 个人使用或小规模分享
- ✅ 每天几十到几百次访问
- ✅ 可以接受冷启动延迟
- ✅ 测试和演示项目

### 何时需要升级？

考虑升级到付费套餐（$7/月）如果：
- ❌ 需要始终在线，不能休眠
- ❌ 访问量大（每天数千次）
- ❌ 需要更多计算资源
- ❌ 商业用途

## 安全建议

1. **永远不要提交 `.env` 文件到 Git**
   - 已在 `.gitignore` 中排除
   - 双重检查：`git status` 不应看到 `.env`

2. **定期更换 API 密钥**
   - 特别是如果怀疑泄露时
   - 在 Render 的环境变量中更新

3. **使用私有仓库**
   - GitHub 免费用户可创建私有仓库
   - 保护您的代码和配置

4. **监控使用量**
   - 定期检查 Anthropic API 使用量
   - 设置预算警报避免超支

## 下一步

恭喜！您的应用已经部署成功。接下来可以：

1. **分享链接**：将 Render 提供的 URL 分享给朋友
2. **添加功能**：本地开发新功能，git push 自动部署
3. **监控性能**：使用 LangSmith 查看 LLM 调用情况
4. **优化成本**：监控 API 使用量，优化 prompt

## 备选部署平台

如果 Render 不合适，还可以考虑：

- **Railway**: 类似 Render，也支持 GitHub 自动部署
- **Fly.io**: 提供免费套餐，但配置稍复杂
- **Heroku**: 曾经最流行，但免费套餐已取消
- **Google Cloud Run**: 按使用付费，适合低流量应用
- **AWS Elastic Beanstalk**: 功能强大但配置复杂

## 技术支持

遇到问题？

1. 查看 Render 官方文档：https://render.com/docs
2. 查看 LangChain 文档：https://python.langchain.com/
3. 检查应用日志排查错误
4. 在 Render Community 提问：https://community.render.com/

祝您部署顺利！🚀
