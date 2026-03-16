# Agent-First Dev -- Agentic Coding 知识库

> 面向领域专家的 AI 辅助开发学习路径，改编自 Stanford CS146S 课程。

**目录**: [为什么是现在](#为什么是现在) · [课程的逻辑](#课程的逻辑) · [10 周内容一览](#10-周内容一览) · [模块索引](#模块索引) · [前置要求](#前置要求) · [如何使用](#如何使用这个知识库) · [致谢](#致谢)

## 为什么是现在？

Vibe Coding 工具（v0、bolt.new、Replit Agent 等）让任何人都能在几分钟内生成一个 Demo。但 Demo 不是产品——它没有安全检查、没有错误处理、上线第一天就可能崩溃。

Coding Agent 改变了这个等式。Claude Code、Cursor、Warp 这些工具不再只是"帮你补全代码"，而是可以像一个初级工程师一样，理解项目上下文、遵循工程规范、在整个软件生命周期中协助你工作。

> "Modern AI tooling will not only enhance developer productivity but also democratize software engineering for a broader audience."
> — Stanford CS146S 课程定位

这意味着：如果你是某个领域的专家——医生、律师、金融分析师、运营负责人——你不需要先学三年编程，再去做一个解决自己领域问题的应用。你需要的是学会如何与 AI 协作开发，这正是本知识库教的。

## 课程的逻辑

10 周课程覆盖一个完整的软件生命周期：

```
Phase 1 — 理解 (Week 1-2)     LLM 原理 + 编码代理架构
Phase 2 — 构建 (Week 3-5)     AI IDE + 代理模式 + 现代终端
Phase 3 — 加固 (Week 6-7)     安全扫描 + 代码审查
Phase 4 — 交付 (Week 8)       多技术栈全栈应用
Phase 5 — 运维与未来 (Week 9-10)  监控 + 行业展望
```

**Understand → Build → Harden → Ship → Operate** — 每个阶段都有明确的产出，后一阶段建立在前一阶段的基础上。

## 10 周内容一览

根据你的时间和目标，选择适合的路径：

### 快速路径（4 周）

**Week 1 → 2 → 4 → 8** — 理解提示 → 掌握架构 → 深入代理 → 实战应用。适合有一定开发经验、想快速上手 Agentic Coding 的人。

### 完整路径（10 周）

| 周次 | 主题 | 实践作业 | 嘉宾 |
|------|------|----------|------|
| [Week 1](modules/agentic-coding/week1/README.md) | 提示工程 | 6 种提示技术练习 | — |
| [Week 2](modules/agentic-coding/week2/README.md) | AI 辅助全栈开发 | 用 AI 构建完整 Web 应用 | — |
| [Week 3](modules/agentic-coding/week3/README.md) | MCP 服务器 | 构建 MCP 服务器 | Silas Alberti (Cognition) |
| [Week 4](modules/agentic-coding/week4/README.md) | 自主编码代理 | Claude Code 深度实践 | Boris Cherney (Anthropic) |
| [Week 5](modules/agentic-coding/week5/README.md) | Warp Agentic 开发 | 多代理工作流 | Zach Lloyd (Warp) |
| [Week 6](modules/agentic-coding/week6/README.md) | 安全扫描 | Semgrep 安全检查 | Isaac Evans (Semgrep) |
| [Week 7](modules/agentic-coding/week7/README.md) | AI 代码审查 | 人机协作代码审查 | Tomas Reimers (Graphite) |
| [Week 8](modules/agentic-coding/week8/README.md) | 多技术栈应用 | 三种技术栈构建同一应用 | Gaspar Garcia (Vercel) |
| [Week 9](modules/agentic-coding/week9/README.md) | AI 系统监控 | 阅读 + 自学实践 | Mayank Agarwal & Milind Ganjoo (Resolve AI) |
| [Week 10](modules/agentic-coding/week10/README.md) | AI 软件工程的未来 | 阅读 + 自学实践 | Martin Casado (a16z) |

### 深度路径

完成全部 10 周内容，并深入每个模块的扩展资源和参考文献。适合想深入理解原理、未来可能转向技术岗位的学习者。

---

## 模块索引

```
agent-first-dev/
  modules/
    agentic-coding/       -- 核心模块，基于 Stanford CS146S 课程内容
    app-dev-fundamentals/  -- 应用开发基础（规划中）
    getting-started/       -- 入门指南（规划中）
  guides/                 -- 跨模块实用指南
  resources/              -- 学习资源汇总
```

| 目录 | 说明 | 状态 |
|------|------|------|
| [`modules/agentic-coding/`](modules/agentic-coding/README.md) | 核心模块：AI 辅助编码、提示工程、全栈开发、安全与部署 | 进行中 |
| [`modules/app-dev-fundamentals/`](modules/app-dev-fundamentals/README.md) | 应用开发基础：数据库、API、前后端概念 | 规划中 |
| [`modules/getting-started/`](modules/getting-started/README.md) | 入门指南：环境搭建、工具选择、第一个项目 | 规划中 |
| [`guides/`](guides/README.md) | 跨模块实用指南（如何选 AI 工具、如何调试等） | 规划中 |
| [`resources/`](resources/README.md) | 学习资源汇总：推荐阅读、视频、社区 | 规划中 |

---

## 前置要求

- 基本的电脑操作能力（会用浏览器、安装软件）
- 愿意学习新事物的心态
- **不需要**任何编程经验
- **不需要**计算机科学背景

---

## 如何使用这个知识库

1. **先选路径**：根据上面的学习路径选择适合自己的节奏
2. **从 `modules/agentic-coding/` 开始**：这是核心内容，按周次顺序阅读
3. **遇到不懂的术语**：查阅根目录下的 [`TERMINOLOGY.md`（术语表）](TERMINOLOGY.md)
4. **跳过可以跳过的**：如果某个模块你已经熟悉，直接跳到下一个
5. **动手做项目**：每周都有练习，建议跟着做，光读不练效果减半

---

## 致谢

本知识库改编自 Stanford CS146S 课程，由 Mihail Eric 主讲。

- 原始课程网站: [The Modern Software Developer](https://themodernsoftware.dev)
- 课程设计和原始内容版权归 Stanford / Mihail Eric 所有

感谢原作者将课程内容开放，使得这样的改编和二次创作成为可能。

---

## 许可协议

本项目内容基于 Stanford CS146S 课程改编，请遵守原始课程的许可条款。本知识库中新增的内容以开源方式提供，具体许可证见项目根目录下的 LICENSE 文件（如有）。
