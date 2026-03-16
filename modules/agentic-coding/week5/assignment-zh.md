> [← 本周导航](README.md) · [模块首页](../README.md) · [术语表](../../../TERMINOLOGY.md)

# Week 5 中文导读：Warp 环境下的 Agentic 开发

## 这周在干什么

这周和 Week 4 的目标相似——构建开发自动化，但换了一个工具：Warp。你会发现不同的 AI 开发环境有不同的优势，关键是理解底层思路而非绑定某个工具。

如果你做完 Week 4 觉得"我已经掌握了 AI 辅助自动化的核心思路"，那这周可以快速浏览。但如果你对"多代理协作"这个概念好奇，这周有一些独特的内容值得深入。

---

## Week 5 vs Week 4 的关系

可以把 Week 4 和 Week 5 想成"用不同品牌的厨房设备做同一道菜"。核心理念（自动化、AI 协作）是一样的，但具体操作方式不同。这种对比本身就是一种学习——让你理解哪些是"通用能力"，哪些是"工具特有功能"。

通用能力的例子：
- 把重复操作封装成可复用的流程
- 用自然语言描述任务，让 AI 执行
- 在开发流程中集成自动检查

工具特有功能的例子：
- Claude Code 的 `/` 命令和 CLAUDE.md 配置
- Warp 的 Warp Drive 和多标签页代理

认识到这个区别很重要。当你换工具时，通用能力可以直接迁移，而工具特有功能需要重新学习。

---

## Warp 是什么

Warp 是一个现代化的终端（Terminal）应用，内置 AI 功能。相比传统终端（黑色窗口敲命令），Warp 提供了：

- **内置的 AI 对话能力**：不需要额外安装插件，直接在终端中和 AI 对话
- **Warp Drive**：保存和共享提示（Prompts）、规则（Rules）、工作流（Workflows）。可以理解为"终端版的书签和模板库"
- **多标签页/多代理**：可以在不同的标签页中同时运行不同的 AI 代理（Agent），每个代理处理不同的任务

简单来说，如果 Claude Code 是"在终端里加了一个 AI 助手"，那 Warp 是"把整个终端重新设计，让 AI 成为原生体验的一部分"。

---

## 核心概念：多代理工作流（Multi-Agent Workflow）

这是这周最有价值的概念，即使你不打算长期使用 Warp，这个思路也值得理解。

### 基本想法

想象一个团队在同时工作：一个人在写代码，一个人在写测试，一个人在更新文档。他们各自独立工作，最后合并成果。

在 Warp 中，你可以在不同的终端标签页中启动不同的 AI 代理，让它们同时处理不同的任务。比如：

- 标签页 1：AI 代理 A 在实现一个新功能
- 标签页 2：AI 代理 B 在给现有代码写测试
- 标签页 3：AI 代理 C 在更新 API 文档

这比一个 AI 代理串行处理所有任务要快得多。

### 关键挑战：冲突

多代理并行工作听起来很美，但有一个实际问题：如果两个代理同时修改同一个文件怎么办？

这就像两个人同时编辑同一个 Google Doc 的同一段话——结果不可预测。

解决思路有几种：
1. **任务隔离**：确保不同的代理处理不同的文件，避免冲突
2. **顺序依赖**：先让代理 A 完成，再让代理 B 基于 A 的成果工作
3. **git worktree**：给每个代理一个独立的工作目录副本（下面详细说）

---

## git worktree 简介

`git worktree` 是 Git 提供的一个功能，允许你从同一个仓库创建多个工作目录。每个工作目录可以在不同的分支上工作，而且它们共享同一个 Git 历史。

举个例子，假设你的项目在 `/projects/my-app`：

```bash
# 创建一个新的工作目录，基于新分支 feature-a
git worktree add ../my-app-feature-a -b feature-a

# 创建另一个工作目录，基于新分支 feature-b
git worktree add ../my-app-feature-b -b feature-b
```

现在你有三个目录：
- `/projects/my-app` — 主工作目录
- `/projects/my-app-feature-a` — 代理 A 在这里工作
- `/projects/my-app-feature-b` — 代理 B 在这里工作

每个代理在自己的目录里随便改，不会影响其他代理。最后通过 Git 的合并（merge）功能把成果整合到一起。

这就是多代理协作中避免冲突的"物理隔离"方案。

---

## 任务导读

原始作业（assignment.md）要求你完成两个部分：

### Part A：使用 Warp Drive

Warp Drive 是 Warp 的特色功能之一，你可以用它来：
- 保存常用的提示（Prompts），下次直接调用
- 设置规则（Rules），让 AI 按照你的偏好工作
- 集成 MCP 服务器（Model Context Protocol），扩展 AI 的能力

这和 Week 4 中你在 Claude Code 里设置 CLAUDE.md、创建自定义命令的思路是一样的——都是在"教 AI 按照你的方式工作"。

### Part B：多代理工作流

这是这周的重头戏。你需要：
1. 设计一个可以拆分的任务（比如"给这个项目添加一个功能 + 写测试 + 更新文档"）
2. 在 Warp 的多个标签页中启动不同的代理
3. 让它们同时工作
4. 处理可能出现的冲突
5. 合并最终成果

做这个任务时，重点不是最终产出物有多精美，而是体会多代理协作的过程——哪些环节顺畅，哪些地方需要人类干预。

---

## 环境准备

### 1. 安装 Warp 终端

从 [warp.dev](https://www.warp.dev/) 下载并安装 Warp。

### 2. 学习资源

推荐先浏览 [Warp University](https://www.warp.dev/university?slug=university)，了解 Warp 的核心功能和使用方式。

### 3. 启动 Starter 应用

和 Week 4 一样，本周也有一个配套的练习应用。启动步骤：

```bash
# 激活 conda 环境
conda activate cs146s

# （可选）安装 pre-commit hooks
pre-commit install

# 从 week5/ 目录启动应用
make run
```

启动后访问 `http://localhost:8000` 查看前端，`http://localhost:8000/docs` 查看 API 文档。

### 4. 应用结构说明

```
backend/                # FastAPI 后端应用
frontend/               # 静态前端（由 FastAPI 托管）
data/                   # SQLite 数据库 + 种子数据
docs/                   # 代理驱动工作流的任务列表（TASKS.md）
```

先花几分钟浏览应用的现有功能，熟悉项目结构后再开始做任务。

---

## 练习任务

### Part A：Warp Drive 功能（至少完成 1 个）

创建可共享的 Warp Drive 提示（Prompt）、规则（Rule）或 MCP 服务器集成。示例方向：

- **测试运行器**：运行测试并显示覆盖率（Coverage），自动重试不稳定的测试（Flaky Test）
- **文档同步**：从 `/openapi.json` 生成或更新 `docs/API.md`，列出路由变化
- **重构工具**：重命名模块（Module），自动更新导入（Import），运行 lint 和测试验证
- **发布助手**：更新版本号（Version Bump），运行检查，生成变更日志（Changelog）
- **集成 Git MCP 服务器**：让 Warp 自主操作 Git（创建分支、提交、生成 PR 说明等）

> 建议：保持工作流聚焦，使用参数传递（而非硬编码），保持幂等性（Idempotent），优先使用非交互式步骤。

### Part B：多代理工作流（至少完成 1 个）

在 Warp 的不同标签页（Tab）中运行多个代理（Agent），同时处理不同的独立任务：

1. 从 `week5/docs/TASKS.md` 中选择多个任务
2. 在不同的 Warp 标签页中启动并发代理
3. 挑战：你能同时运行多少个代理？
4. 提示：`git worktree` 可以帮助避免代理之间的文件冲突（参见上文 "git worktree 简介"）

### Part II：使用自动化

用你在 Part A 和 Part B 中构建的自动化来改进工作流程。记录每个自动化解决了什么痛点（Pain Point）或加速了什么过程。

**注意**：所有工作限制在 `week5/` 目录内（backend, frontend, logic, tests）。

---

## 自检清单

- [ ] 理解 Warp 和其他 AI 开发工具（如 Claude Code）的异同
- [ ] 成功创建了至少一个 Warp 自动化（保存的提示、规则或工作流）
- [ ] 体验了多代理同时工作的场景
- [ ] 理解多代理协作中的冲突问题和解决思路（如 git worktree）
- [ ] 能说出"工具不同但方法论相同"的具体例子

[开始 Week 6 →](../week6/README.md)
