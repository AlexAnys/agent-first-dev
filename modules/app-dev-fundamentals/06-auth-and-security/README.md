> [← 模块首页](../README.md) · [← 05: API](../05-apis/README.md) · [方法论 →](../methodology/README.md)

# 06: 认证与安全 — 谁是你，你能做什么

> 一句话：认证（Authentication）= 证明你是谁；授权（Authorization）= 你被允许做什么。

## 为什么 Coding Agent 用户需要懂这个

Every real application has users. "Add user login" is one of the most common requests to AI, but if you don't understand the concepts, you can't evaluate if AI's implementation is secure. Security mistakes are the most costly mistakes in software.

## 核心心智模型

### 认证 vs 授权

**认证（Authentication）**: 你是谁？
- 用户名 + 密码 → 登录
- 类比：进大楼时出示工牌

**授权（Authorization）**: 你能做什么？
- 普通用户只能看自己的数据，管理员能看所有数据
- 类比：你的工牌能刷开哪些门

### Session 和 Cookie：记住你是谁

1. 你登录（提交用户名密码）
2. 服务器验证成功，生成一个 Session ID
3. 把 Session ID 通过 Cookie 存到你的浏览器里
4. 之后每次请求，浏览器自动带上这个 Cookie
5. 服务器通过 Cookie 认出你，不需要再次登录

Cookie 就是浏览器里的一个小文本文件，仅此而已。

### 常见的认证方式

- 用户名 + 密码（最传统）
- OAuth（"用 Google 账号登录"）
- API Key（程序之间的认证，05 已提到）

### 安全的基本原则

- 永远不要明文存储密码（用哈希）
- HTTPS = 加密传输（HTTP + 锁）
- 最小权限原则：只给用户需要的权限
- 永远不要信任用户输入（SQL 注入、XSS）

## 常见误区

1. "安全可以后面再加" — 安全必须从第一天就考虑
2. "用了框架就自动安全" — 框架帮你处理了很多，但你需要正确使用它
3. "AI 生成的代码是安全的" — 不一定，这是你必须亲自检查的部分

## 这个概念在 Agentic Coding 中的应用

Link to Week 6 (安全扫描 — 用 AI 检查 AI 生成代码的安全性) — this is exactly why Week 6 exists

## 下一步

→ 方法论：这门课是怎么教的
