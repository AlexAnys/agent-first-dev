> [← 模块首页](../README.md) · [← Week 2: AI 辅助全栈开发](../week2/README.md) · [Week 4: 自主编码代理 →](../week4/README.md) · [术语表](../../../TERMINOLOGY.md)

# Week 3: MCP 服务器（Model Context Protocol）

设计并构建一个 MCP 服务器，让 AI 能够连接和使用外部服务。

## 适合谁

- 想理解 AI 如何"使用工具"的人
- 对 AI 生态系统感兴趣的人

## 前置条件

- 完成 Week 1-2（理解提示技术和基本的应用结构）
- 了解 API 的基本概念（Week 2 已涉及）

## 预计时间

6-8 小时（需要查阅 MCP 文档），4-5 小时（有 API 开发经验）

## 课程讲义

[本周讲义 Slides](https://themodernsoftware.dev/) — 本周主题：The AI IDE
<!-- TODO: 替换为 Google Slides 直链 -->

## 前置阅读

1. [MCP Introduction](https://stytch.com/blog/model-context-protocol-introduction/) — MCP 协议入门：什么是 Model Context Protocol
2. [APIs Don't Make Good MCP Tools](https://www.reillywood.com/blog/apis-dont-make-good-mcp-tools/) — 为什么不能简单地把 API 包装成 MCP 工具

## 学习顺序

按以下顺序学习本周内容：

1. **浏览课程讲义** → 见上方[课程讲义](#课程讲义)（快速翻阅，了解本周框架）
2. **阅读前置材料** → 见上方[前置阅读](#前置阅读)
3. **阅读并完成中文指南** → [assignment-zh.md](assignment-zh.md) — MCP 概念 + 环境准备 + 练习任务（完整中文版）
4. **记录学习笔记** → [writeup-zh.md](writeup-zh.md) — 结构化笔记模板
5. **（可选）深入阅读** → 见下方[背景扩展阅读](#背景扩展阅读)
6. **进入下一周** → [Week 4: 自主编码代理](../week4/README.md)

## 文件索引

| 文件 | 说明 |
|------|------|
| [assignment-zh.md](assignment-zh.md) | 中文学习指南（概念解释 + 环境准备 + 练习任务） |
| [writeup-zh.md](writeup-zh.md) | 学习笔记模板 |

> 本周也提供英文原版课程材料（[assignment.md](assignment.md)），可作为对比参考。所有内容已完整覆盖在中文指南中，无需额外阅读。

## 背景扩展阅读

1. [MCP Server Examples](https://github.com/modelcontextprotocol/servers) — 官方 MCP 服务器示例集
2. [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) — MCP 的 TypeScript 开发套件
3. [Cloudflare MCP Server Authentication](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#add-authentication) — Cloudflare 上的 MCP 认证指南

## 跳过指引

如果走快速路径，可以只阅读 assignment-zh.md 中的 MCP 概念部分，理解"AI 如何连接外部工具"的思路，然后直接进入 Week 4。Week 4 会在实践中用到 MCP。

---

[← Week 2: AI 辅助全栈开发](../week2/README.md) · [Week 4: 自主编码代理 →](../week4/README.md)
