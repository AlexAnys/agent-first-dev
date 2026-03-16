> [← 返回首页](../../README.md) · [术语表](../../TERMINOLOGY.md)

# Agentic Coding — 与 AI 协作的软件开发

> 本模块内容基于 Stanford CS146S: The Modern Software Developer 课程（https://themodernsoftware.dev），由 Mihail Eric 设计。原课程文件（assignment.md、writeup.md 及代码）完整保留。中文适配文件为本项目新增。

## 这门课到底教什么？

一句话概括：**Human-agent engineering, not vibe coding.**

"Vibe coding" 这个词最近很火——打开 AI，随便说两句，让它帮你把代码写了。听起来很爽，但现实是：这样写出来的代码你自己都不敢上线。

这个模块教的是另一回事：如何像一个工程师一样，有效地与 AI 协作（collaborate）。你需要理解 AI 在做什么，知道什么时候该信任它、什么时候该纠正它，以及如何设计工作流让人和 AI 各自发挥所长。

说白了，AI 是你的搭档，不是你的替身。

## 10 周课程索引

| 周次 | 主题 | 简介 |
|------|------|------|
| [Week 1](week1/README.md) | 提示工程（Prompt Engineering） | 6 种核心提示技术，从零开始学会跟 AI 说话 |
| [Week 2](week2/README.md) | AI 辅助全栈开发（Full-Stack Development） | 用 AI 构建一个完整的应用，体验端到端的开发流程 |
| [Week 3](week3/README.md) | MCP 服务器（Model Context Protocol） | 扩展 AI 的能力边界，让它能调用外部工具和数据 |
| [Week 4](week4/README.md) | 自主编码代理（Autonomous Coding Agent） | Claude Code 深度实践，理解代理式开发的核心理念 |
| [Week 5](week5/README.md) | Warp 环境下的 Agentic 开发 | 多代理工作流（multi-agent workflow），让多个 AI 协同工作 |
| [Week 6](week6/README.md) | 安全扫描（Security Scanning） | AI 辅助的代码安全检查，把漏洞扼杀在开发阶段 |
| [Week 7](week7/README.md) | AI 代码审查（Code Review） | 人机协作的质量保障，建立可靠的审查流程 |
| [Week 8](week8/README.md) | 多技术栈应用（Multi-Stack Application） | Vibe Coding 的正确打开方式——有章法、有质量地快速开发 |
| [Week 9](week9/README.md) | AI 系统监控（Agents Post-Deployment） | 生产环境监控与 AI 辅助事件响应（阅读 + 自学） |
| [Week 10](week10/README.md) | AI 软件工程的未来（What's Next） | 行业展望与持续学习路径（阅读 + 自学） |

## 课程的逻辑线

10 周课程按 **Understand → Build → Harden → Ship → Operate** 的顺序组织，覆盖完整的软件生命周期：

| 阶段 | 周次 | 你会学到 |
|------|------|----------|
| **理解** | Week 1-2 | LLM 的工作原理、提示技术、编码代理的架构。先理解工具，再使用工具。 |
| **构建** | Week 3-5 | MCP 扩展 AI 能力、Claude Code 的代理模式、Warp 多代理协作。从单点工具到系统化工作流。 |
| **加固** | Week 6-7 | AI 生成代码的安全扫描、人机协作的代码审查。写出来的代码要经得起检验。 |
| **交付** | Week 8 | 多技术栈全栈应用。把前 7 周的能力综合运用，交付一个完整项目。 |
| **运维与未来** | Week 9-10 | 生产环境监控、事件响应、行业趋势。软件上线不是终点，而是另一个起点。 |

## 学习路径

不是所有人都有 10 周时间从头学到尾。根据你的情况，选一条适合自己的路：

### 快速路径（4 周）

**Week 1 → Week 2 → Week 4 → Week 8**

理解提示 → 掌握架构 → 深入代理 → 实战应用。如果你已经有一定的开发经验，想尽快上手 Agentic Coding 的核心技能，走这条路就够了。

### 完整路径（10 周）

按顺序完成所有周。每周大概需要 5-8 小时，适合想系统学习的同学。这是最推荐的方式。

### 深度路径

完整路径 + 每周的扩展阅读和额外练习。适合想深入理解底层原理、未来打算在这个方向深耕的同学。

## 课程嘉宾

| 周次 | 嘉宾 | 身份 |
|------|------|------|
| Week 3 | Silas Alberti | Cognition（Devin）研究负责人 |
| Week 4 | Boris Cherney | Anthropic，Claude Code 创建者 |
| Week 5 | Zach Lloyd | Warp CEO |
| Week 6 | Isaac Evans | Semgrep CEO |
| Week 7 | Tomas Reimers | Graphite CPO |
| Week 8 | Gaspar Garcia | Vercel AI 研究负责人 |
| Week 9 | Mayank Agarwal & Milind Ganjoo | Resolve AI CTO & Technical Staff |
| Week 10 | Martin Casado | a16z 合伙人 |

## 导航

- [Week 1 — 提示工程](week1/README.md)
- [Week 2 — AI 辅助全栈开发](week2/README.md)
- [Week 3 — MCP 服务器](week3/README.md)
- [Week 4 — 自主编码代理](week4/README.md)
- [Week 5 — Warp 环境下的 Agentic 开发](week5/README.md)
- [Week 6 — 安全扫描](week6/README.md)
- [Week 7 — AI 代码审查](week7/README.md)
- [Week 8 — 多技术栈应用](week8/README.md)
- [Week 9 — AI 系统监控](week9/README.md)
- [Week 10 — AI 软件工程的未来](week10/README.md)

---

[← 返回首页](../../README.md) · [术语表](../../TERMINOLOGY.md) · [部署指南](../../guides/deployment-cn.md)
