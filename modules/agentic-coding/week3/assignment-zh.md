> [← 本周导航](README.md) · [模块首页](../README.md) · [术语表](../../../TERMINOLOGY.md)

# Week 3 中文导读：构建 MCP 服务器

## 这周要做什么

这周你要构建一个 MCP 服务器——让 AI 能够"伸出手"去操作外部系统。这是 AI 从"只能聊天"变成"能做事"的关键技术。

如果说 Week 1 让 AI 学会了"说话"，Week 2 让 AI 学会了"做事"，那 Week 3 就是让 AI 学会"连接外部世界"。

---

## MCP 是什么？日常类比

想象你请了一个非常聪明的助理，但他被锁在一个没有网络、没有电话的房间里。他能帮你分析问题、写报告，但不能帮你查天气、订机票、发邮件。

MCP 就是给这个房间装上"标准接口"——电话线、网线、传真机。通过这些接口，助理可以：

- 查询外部信息（天气、股票、新闻）
- 操作外部系统（发邮件、创建日程、管理文件）
- 访问数据库或 API

关键词是"标准"。MCP 定义了一套统一的协议（Protocol），让不同的 AI 工具（Claude、Cursor 等）可以用同样的方式连接外部服务。这就像 USB 接口统一了各种设备的连接方式一样——你不需要为每个设备设计专门的插头。

---

## MCP 的三大能力

### Tools（工具）

AI 可以调用的操作。比如"查询天气"、"创建 GitHub Issue"、"发送 Slack 消息"。

工具是最常用的能力。你定义一个工具，告诉 AI 这个工具叫什么、接收什么参数、返回什么结果，AI 就可以在需要的时候调用它。

### Resources（资源）

AI 可以读取的数据。比如数据库中的记录、文件内容、配置信息。

Resources 和 Tools 的区别：Tools 是"做事"（有副作用），Resources 是"读数据"（只读）。这个区分让客户端可以更放心地让 AI 读取 Resources，而对 Tools 的调用加上确认步骤。

### Prompts（提示模板）

预定义的对话模板，简化常见操作。比如你可以定义一个"代码审查"的 Prompt 模板，用户选择后 AI 就按照固定的流程来审查代码。

说实话，Prompts 在实际使用中不如 Tools 和 Resources 常见。如果时间有限，先把 Tools 搞明白就行。

---

## 传输方式（Transport）

MCP 服务器和 AI 客户端之间需要通信，有两种主要方式：

### STDIO（本地模式）

服务器和 AI 在同一台机器上运行，通过标准输入/输出（stdin/stdout）通信。

- 优点：简单、安全，不需要网络配置
- 缺点：只能本地使用
- 适合：学习、个人工具

### HTTP（远程模式）

服务器部署在网络上，AI 通过 HTTP 请求调用。现在的标准实现使用 Streamable HTTP（之前叫 SSE）。

- 优点：可以多人共享、远程访问
- 缺点：需要处理认证、网络安全等问题
- 适合：团队工具、生产环境

建议这周先用 STDIO 模式，把核心概念搞清楚。HTTP 模式可以作为进阶挑战。

---

## 任务导读

原课程要求你构建一个 MCP 服务器。下面是关键步骤的中文解读：

### 1. 选择一个外部 API

选一个你感兴趣的领域。几个建议：

- **天气 API**（如 OpenWeatherMap）：简单，适合入门
- **GitHub API**：如果你是开发者，这个很实用
- **新闻 API**（如 NewsAPI）：数据丰富，适合练习
- **任何你工作中用得上的 API**：最好的学习就是做有用的东西

### 2. 实现至少 2 个 MCP 工具

每个工具需要定义：

- 名称和描述（AI 通过这些来决定什么时候调用）
- 输入参数（JSON Schema 格式）
- 处理逻辑（调用外部 API、处理返回数据）
- 返回结果（格式化为 AI 能理解的文本）

工具的描述特别重要——AI 是通过描述来决定什么时候调用哪个工具的。写得不好，AI 就不知道什么时候该用它。

### 3. 编写文档和使用说明

好的 MCP 服务器需要清晰的 README：怎么安装、怎么配置、提供了什么工具。

### 4. （可选）添加认证功能

如果你的外部 API 需要 API Key，考虑怎么安全地管理这些密钥。

---

## MCP 生态概览

目前支持 MCP 的主要客户端：

- **Claude Desktop**：Anthropic 的桌面应用，原生支持 MCP
- **Claude Code**：命令行工具，通过 `claude mcp add` 配置 MCP 服务器
- **Cursor**：AI 代码编辑器，支持 MCP

社区已经有很多现成的 MCP 服务器可以参考和使用。官方维护的列表在 [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)，涵盖了文件系统、数据库、GitHub、Slack 等各种集成。

浏览这个列表是个很好的学习方式——看看别人怎么设计 MCP 服务器，然后模仿着做自己的。

---

## 与主题线的连接

> Week 1 学了"怎么说话"，Week 2 学了"怎么做事"，Week 3 学的是"怎么连接外部世界"。MCP 是 Agentic Coding 生态的重要基础设施。在 Week 4 中，你会看到 Claude Code 如何利用 MCP 服务器来扩展自己的能力。

MCP 之所以重要，是因为它解决了一个关键问题：AI 模型本身不能访问你的数据、不能操作你的系统。MCP 提供了一种标准化的方式来"给 AI 装上手和眼"。没有这个，AI 就只是一个关在房间里的聪明人。

---

## 环境准备

### 1. 安装 MCP SDK

Python 环境下安装：

```bash
pip install mcp
```

或参考官方文档获取最新安装方式。

### 2. 获取外部 API Key

选择一个你感兴趣的外部 API，注册并获取 API Key（如果该 API 需要认证）。

### 3. 准备 MCP 客户端

推荐使用 Claude Desktop 作为 MCP 客户端来测试你的服务器。也可以使用 Claude Code（通过 `claude mcp add` 命令配置）或 Cursor。

---

## 练习任务

### 1. 选择一个外部 API

从以下领域中选择一个你感兴趣的 API（或任何你工作中用得上的 API）：

- 天气（如 OpenWeatherMap）
- GitHub Issues
- Notion 页面
- 电影/电视数据库（如 TMDB）
- 日历
- 任务管理（如 Todoist）
- 金融/加密货币
- 旅行
- 体育数据

### 2. 实现至少 2 个 MCP 工具（Tool）

每个工具需要包含类型化参数（typed parameters）和错误处理（error handling）。工具的描述要写得清晰准确，因为 AI 是通过描述来决定什么时候调用哪个工具的。

### 3. 基本健壮性

- HTTP 失败、超时、空结果的优雅处理（graceful error handling）
- API 限流处理（rate limiting）：简单的退避策略（backoff）或用户提示

### 4. 文档和打包

- 清晰的安装说明
- 环境变量配置（如 API Key 设置方式）
- 运行命令
- 示例调用流程（在客户端中如何触发你的工具）

### 5. 选择部署模式

- **本地模式 (STDIO)**：在本机运行，可被 Claude Desktop 或 Cursor 发现
- **远程模式 (HTTP)**：部署到网络，可被 MCP 客户端远程调用（加分项）

### 6. （可选加分）认证

- API Key 支持：通过环境变量和客户端配置
- 或 OAuth2 Bearer Token（适用于 HTTP 传输模式）

---

## 代码结构建议

- 建议放在 `week3/server/` 目录，入口文件 `main.py` 或 `app.py`
- 需要创建 `week3/README.md`（注意：这里指的是你的 MCP 服务器文档，不是本导航 README）
- README 中需要包含：前置条件、环境配置、运行说明、客户端配置方法、工具参考（名称、参数、示例输入输出）

---

## 参考资源

- MCP 服务器快速入门: [modelcontextprotocol.io/quickstart/server](https://modelcontextprotocol.io/quickstart/server)（注意：不能直接提交这个示例）
- MCP 授权规范 (HTTP): [modelcontextprotocol.io/specification/2025-06-18/basic/authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- Cloudflare Remote MCP: [developers.cloudflare.com/agents/guides/remote-mcp-server/](https://developers.cloudflare.com/agents/guides/remote-mcp-server/)
- Vercel MCP 部署: [vercel.com/docs/mcp/deploy-mcp-servers-to-vercel](https://vercel.com/docs/mcp/deploy-mcp-servers-to-vercel)

---

## 完成标准

| 类别 | 分值 | 要求 |
|------|------|------|
| 功能 (Functionality) | 35 分 | 2+ 工具实现、正确的 API 集成、有意义的输出 |
| 可靠性 (Reliability) | 20 分 | 输入验证、错误处理、日志记录、限流处理 |
| 开发体验 (Developer Experience) | 20 分 | 清晰的文档、容易运行、合理的目录结构 |
| 代码质量 (Code Quality) | 15 分 | 可读性、命名规范、类型提示（type hints） |
| 加分 (Extra Credit) | 10 分 | 远程 HTTP 部署 +5，认证实现 +5 |

---

## 自检清单

- [ ] 能用自己的话解释 MCP 是什么、为什么需要它
- [ ] 理解 Tools、Resources、Prompts 三大概念
- [ ] 成功构建了一个可运行的 MCP 服务器
- [ ] 能在 Claude Desktop 或其他客户端中测试你的服务器
- [ ] 理解 STDIO 和 HTTP 两种传输方式的区别

---

[开始 Week 4 →](../week4/README.md)
