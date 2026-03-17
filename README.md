# Agent-First Dev

> 与 Coding Agent 协作构建生产级应用的最小必要知识。基于 [Stanford CS146S](https://themodernsoftware.dev)（授权）和 Chicago Booth Application Development 课程。

**目录**: [为什么是现在](#为什么是现在) · [模块总览](#模块总览) · [前置要求](#前置要求) · [如何使用](#如何使用这个知识库) · [授权与致谢](#授权与致谢)

## 为什么是现在？

**Coding Agent 的能力已经发生质变。** Claude Code、Cursor 等工具不再只是补全几行代码——它们可以在相当长的时间里自主完成完整的开发任务，包括生产级应用。

但大多数非技术背景的人还卡在 vibe coding 阶段：用 lovable、manus、v0 生成一个 Demo，看起来能跑，实际上线第一天就崩。与此同时，市面上铺天盖地的 AI 工具推荐和教程，噪音远大于信号，根本分不清该学什么、不该学什么。

**这个知识库要解决的就是这个问题。**

我们从 Stanford 和 Chicago Booth 两门顶级课程中提取出与 Coding Agent 协作进行全栈开发的**最小必要信息**——不是让你学三年编程，而是在你需要的时候，给你刚好够用的知识，让你能真正构建可用的软件。

---

## 模块总览

知识库按模块组织，每个模块聚焦一个完整主题。

| 模块 | 说明 | 状态 |
|------|------|------|
| [**Agentic Coding**](modules/agentic-coding/README.md) | 与 AI 协作的软件开发（改编自 Stanford CS146S，10 周） | **进行中** |
| [App Dev Fundamentals](modules/app-dev-fundamentals/README.md) | 应用开发基础：数据库、API、前后端概念 | 规划中 |
| [Getting Started](modules/getting-started/README.md) | 入门指南：环境搭建、工具选择、第一个项目 | 规划中 |

| 其他资源 | 说明 |
|----------|------|
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

## 模块 2: App Dev Fundamentals（规划中）

> 应用开发基础：数据库、API、前后端概念。为没有开发背景的领域专家补齐必要的技术基础。
>
> → [模块首页](modules/app-dev-fundamentals/README.md)

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

- **BY**（署名）— 使用或改编本内容时，请注明出处并链接到本仓库和[原课程](https://themodernsoftware.dev)
- **NC**（非商业）— 不得用于商业目的
- **SA**（相同方式共享）— 改编作品须以相同协议发布
