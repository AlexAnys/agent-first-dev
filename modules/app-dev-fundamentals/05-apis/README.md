> [← 模块首页](../README.md) · [← 04: 数据库与 CRUD](../04-databases-and-crud/README.md) · [06: 认证与安全 →](../06-auth-and-security/README.md)

# 05: API — "一切都是 HTTP 请求"

> 一句话：你的应用要查天气、发短信、调用 AI？都是发一个 HTTP 请求，拿回一段数据。

## 为什么 Coding Agent 用户需要懂这个

AI coding agents themselves are APIs. When you use Claude Code, it sends HTTP requests to Claude's API. When you ask AI to "integrate weather data", it needs to make API calls. Understanding this pattern demystifies both AI and external services.

## 核心心智模型

### API = 程序之间的对话方式

- 你的应用想知道明天的天气 → 发一个请求给天气 API
- 天气 API 返回一段 JSON 数据 → 你的应用解析并展示

和浏览器访问网页一模一样（01 已学），只是：
- 浏览器请求 → 返回 HTML（给人看）
- 程序请求 API → 返回 JSON（给程序读）

### JSON：机器的通用语言

```json
{
  "city": "上海",
  "temperature": 22,
  "condition": "晴"
}
```

JSON 就是一种结构化的文本格式。所有 API 都用它。
理解 JSON 不需要编程经验——它就是"键:值"对。

### API 的核心要素

1. **端点（Endpoint）**: URL 地址，比如 `api.weather.com/forecast`
2. **方法（Method）**: GET（查询）或 POST（提交数据）
3. **认证（Auth）**: API Key 或 Token，证明你有权限
4. **请求体（Body）**: 你发送的数据（POST 时需要）
5. **响应（Response）**: 返回的 JSON 数据

### "AI 调用"被去神秘化

调用 ChatGPT/Claude API 和调用天气 API 在技术上完全一样：

1. 发一个 POST 请求到 API 端点
2. 带上 API Key
3. 请求体里放你的 prompt
4. 拿回 JSON 格式的回复

## 常见误区

1. "API 很高级" — 它就是 01 学过的 HTTP 请求，只是返回 JSON 而非 HTML
2. "每个 API 都不一样" — 核心模式完全相同：endpoint + method + auth + body → response
3. "AI 代理会自己处理 API" — AI 需要知道 endpoint 和认证方式，这是你要告诉它的

## 这个概念在 Agentic Coding 中的应用

[Agentic Coding Week 3](../../agentic-coding/week3/README.md) (MCP 本质上就是标准化的 API 协议) and [Agentic Coding Week 5](../../agentic-coding/week5/README.md) (多代理工作流中代理之间的通信也是 API)

## 动手试一试

### 练习 1：在浏览器里调用 API
直接在浏览器地址栏输入以下 URL，你就在调用 API 了：

- **查天气数据**：`https://wttr.in/Shanghai?format=j1` → 返回上海天气的 JSON（注意 `?format=j1` 参数不能省，没有它返回的是网页而不是 JSON）
- **查 GitHub 用户**：`https://api.github.com/users/AlexAnys` → 返回 GitHub 用户信息
- **查随机名言**：`https://dummyjson.com/quotes/random` → 返回一条随机名言

观察返回的 JSON 数据，找到你感兴趣的字段。这就是"调用 API"——没什么魔法，就是访问一个 URL，拿回一段结构化数据。

### 练习 2：用 Hoppscotch 发送 POST 请求
打开 [Hoppscotch](https://hoppscotch.io/) — 一个免费的 API 测试工具（不需要注册）：

1. 把方法改为 **POST**
2. URL 填入 `https://jsonplaceholder.typicode.com/posts`
3. 点击 **Body** → 选 **application/json**，填入：
```json
{
  "title": "我的第一个 API 请求",
  "body": "这是通过 POST 发送的数据",
  "userId": 1
}
```
4. 点 **Send** → 看返回结果

你刚刚完成了一个 POST 请求——和"提交表单"、"调用 AI API"在技术上完全一样。

以上练习的核心启示：当你的应用"调用 ChatGPT"时，技术上发生的事情和练习 2 一模一样——发一个 POST 请求，body 里放 prompt，拿回 JSON 格式的回复。

## 下一步

→ 06: 认证与安全

---

[← 04: 数据库与 CRUD](../04-databases-and-crud/README.md) · [06: 认证与安全 →](../06-auth-and-security/README.md)
