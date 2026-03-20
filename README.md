# Agent-First Dev 智能体开发最重要的事

> 与 Coding Agent 协作构建生产级应用的最小必要知识。基于 [Stanford CS146S](https://themodernsoftware.dev)（授权）和 Chicago Booth Application Development 课程。

**目录**: [背景](#背景) · [为什么做这个仓库](#为什么做这个仓库) · [模块总览](#模块总览) · [前置要求](#前置要求) · [如何使用](#如何使用这个知识库) · [授权与致谢](#授权与致谢)

## 背景

> "会写代码还意味着一件事：你有了想法，就能自己动手做出来。这不是必须的（Jeff Bezos 就不会写代码），但这是个巨大的优势。当你琢磨一个点子——比如把大学花名册搬到网上——你的反应不再是'这想法挺有意思'，而是'这想法挺有意思，今晚我就做个初版出来'。"
>
> — Paul Graham, *[How to Get Startup Ideas](http://paulgraham.com/startupideas.html)*（Chicago Booth BUSN 36110 课程开篇引用）

我是一个非技术背景的 MBA 学生。2025 年秋在 Chicago Booth 修了一门 Application Development 课程，从写第一行代码开始。四个月后，我在用 Coding Agent 从零开发生产级的全栈 SaaS 应用。

从今年 2 月到现在，我在 GitHub 上收获了 3800+ Star，利用业余时间同时管理着二十多个开源项目，这超出了以前的想象。

## 为什么做这个仓库

**[25年底以来 Coding Agent 的能力已经发生质变](https://wtfhappened2025.com/)。** Claude Code、Cursor 等工具可以在相当长的时间里自主完成完整的开发任务，包括生产级应用。但大多数非技术背景的人还卡在 vibe coding（随意让 AI 生成代码，不关心质量和可维护性）阶段：用 lovable、manus、v0 生成一个 Demo，看起来能跑，实际上线第一天就崩。

与此同时，市面上铺天盖地的 AI 工具推荐和教程，噪音远大于信号。

**这个仓库就是我回过头来，把最重要的东西整理出来。**

1. **走过的弯路和经验教训** — 哪些知识真正有用，哪些是浪费时间
2. **为什么学习有时候是一种"诅咒"** — 并非知识越多越好，过度学习反而让你不敢动手
3. **最小必要知识** — 从 Stanford 和 Chicago Booth 两门顶级课程中，提取出与 Coding Agent 协作进行全栈开发刚好够用的信息

我的核心信念：**Learn by Doing**。不是先学完再做，而是在做的过程中，只学当下需要的东西。这个仓库会持续更新，分享我对即时学习（Just-in-Time Learning）、知识必要性、以及什么才是 AI 时代学习方式的思考。

> 📖 **[领域专家 × AI 协作框架](FRAMEWORK.md)** — 这些模块背后的方法论体系。关于如何学习、如何思考、如何与 AI 协作的通用框架。也可以直接作为 AI Agent 的上下文，帮助你更有效地学习任何领域。

---

## 模块总览

知识库按模块组织，每个模块聚焦一个完整主题。

| 模块 | 说明 | 状态 |
|------|------|------|
| [**Agentic Coding**](modules/agentic-coding/README.md) | 与 AI 协作的软件开发（改编自 Stanford CS146S，10 周） | **进行中** |
| [**Application Development**](modules/app-dev-fundamentals/README.md) | 理解软件是怎么运作的（基于 Chicago Booth BUSN 36110 核心思想） | **框架已搭建** |
| [Getting Started](modules/getting-started/README.md) | 入门指南：环境搭建、工具选择、第一个项目 | 规划中 |

| 其他资源 | 说明 |
|----------|------|
| [**FRAMEWORK.md**](FRAMEWORK.md) | 领域专家 × AI 协作框架：学习方法论与思维模型（人类参考 + Agent 上下文） |
| [`guides/`](guides/README.md) | 跨模块实用指南（如何选 AI 工具、如何调试等） |
| [`resources/`](resources/README.md) | 学习资源汇总：推荐阅读、视频、社区 |
| [`TERMINOLOGY.md`](TERMINOLOGY.md) | 术语表 |

---

## 模块 1: Agentic Coding

> 改编自 [Stanford CS146S](https://themodernsoftware.dev)，由 Mihail Eric 设计。完整的 10 周课程，覆盖从提示工程到系统监控的软件全生命周期。
>
> → [**模块首页**](modules/agentic-coding/README.md)（课程逻辑、学习路径、嘉宾一览）

| 周次 | 主题 | 一句话简介 |
|------|------|-----------|
| [Week 1](modules/agentic-coding/week1/README.md) | 提示工程 | 6 种核心提示技术，从零开始学会跟 AI 说话 |
| [Week 2](modules/agentic-coding/week2/README.md) | AI 辅助全栈开发 | 用 AI 构建一个完整的 Web 应用 |
| [Week 3](modules/agentic-coding/week3/README.md) | MCP 服务器 | 扩展 AI 的能力边界，让它能调用外部工具和数据 |
| [Week 4](modules/agentic-coding/week4/README.md) | 自主编码代理 | Claude Code 深度实践，理解代理式开发的核心理念 |
| [Week 5](modules/agentic-coding/week5/README.md) | Warp Agentic 开发 | 多代理工作流，让多个 AI 协同工作 |
| [Week 6](modules/agentic-coding/week6/README.md) | 安全扫描 | AI 辅助的代码安全检查 |
| [Week 7](modules/agentic-coding/week7/README.md) | AI 代码审查 | 人机协作的质量保障 |
| [Week 8](modules/agentic-coding/week8/README.md) | 多技术栈应用 | Vibe Coding 的正确打开方式 |
| [Week 9](modules/agentic-coding/week9/README.md) | AI 系统监控 | 生产环境监控与事件响应（阅读 + 自学） |
| [Week 10](modules/agentic-coding/week10/README.md) | AI 软件工程的未来 | 行业展望与持续学习路径（阅读 + 自学） |

**快速路径**: Week 1 → 2 → 4 → 8 · **完整路径**: Week 1-10 · 详见[模块首页](modules/agentic-coding/README.md)

---

## 模块 2: Application Development

> 理解软件是怎么运作的。基于 Chicago Booth BUSN 36110 课程核心思想，用螺旋式学习法构建对 Web 应用的完整心智模型。
>
> → [**模块首页**](modules/app-dev-fundamentals/README.md)（课程思想、教学理念、与 Agentic Coding 的关系）

| 章节 | 主题 | 一句话简介 |
|------|------|-----------|
| [01](modules/app-dev-fundamentals/01-how-the-web-works/README.md) | 互联网是怎么工作的 | HTTP 请求与响应，URL 的工作原理 |
| [02](modules/app-dev-fundamentals/02-data-modeling/README.md) | 数据建模 | 最高杠杆的技能——名词变成表 |
| [03](modules/app-dev-fundamentals/03-request-lifecycle/README.md) | 请求的生命周期 | RCAV: URL 如何变成你看到的页面 |
| [04](modules/app-dev-fundamentals/04-databases-and-crud/README.md) | 数据库与 CRUD | 增删改查——所有应用的骨架 |
| [05](modules/app-dev-fundamentals/05-apis/README.md) | API | "一切都是 HTTP 请求" |
| [06](modules/app-dev-fundamentals/06-auth-and-security/README.md) | 认证与安全 | 谁是你，你能做什么 |
| [方法论](modules/app-dev-fundamentals/methodology/README.md) | 教学理念 | 螺旋学习、砍范围、AI 是乘数 |

---

## 模块 3: Getting Started（规划中）

> 入门指南：环境搭建、工具选择、从零完成第一个项目。
>
> → [模块首页](modules/getting-started/README.md)

---

## 前置要求

- 基本的电脑操作能力（会用浏览器、安装软件）
- 愿意学习新事物的心态
- **不需要**任何编程经验
- **不需要**计算机科学背景

---

## 如何使用这个知识库

1. **选择模块**：从上方[模块总览](#模块总览)选择感兴趣的主题，或直接点进某一周
2. **查看模块首页**：每个模块都有独立的 README，包含课程逻辑、学习路径和推荐顺序
3. **遇到不懂的术语**：查阅 [`TERMINOLOGY.md`（术语表）](TERMINOLOGY.md)
4. **跳过可以跳过的**：如果某个部分你已经熟悉，直接跳到下一个
5. **动手做项目**：每个模块都有练习，建议跟着做，光读不练效果减半

---

## 授权与致谢

本知识库的 Agentic Coding 模块经 Stanford CS146S 课程设计者 [Mihail Eric](https://www.mihaileric.com) 授权，将课程材料翻译并改编为中文学习路径。

- 原始课程网站: [The Modern Software Developer](https://themodernsoftware.dev)
- 原课程内容版权归 Mihail Eric 所有

本项目不是单纯的翻译，而是结合作者在 Chicago Booth Application Development 课程中的实践经验（非技术背景，4 个月内用 AI 辅助开发交付 20+ 开源项目），为非 CS 背景的学习者重新组织的自学路径。

---

## 许可协议

本项目采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 协议。

- **BY**（署名）— 使用或改编本内容时，请注明出处并链接到[本仓库](https://github.com/AlexAnys/agent-first-dev)和[原课程](https://themodernsoftware.dev)
- **NC**（非商业）— 不得用于商业目的
- **SA**（相同方式共享）— 改编作品须以相同协议发布
