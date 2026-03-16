> [← 本周导航](README.md) · [模块首页](../README.md) · [术语表](../../../TERMINOLOGY.md)

# Week 4 中文导读：自主编码代理

## 这周要做什么

这周是整个课程的核心。你将学习如何把 Claude Code 从"一个聊天工具"变成"一个可配置的团队成员"。关键词：自动化、可复用、可协作。

前三周是在学习单项技能，这周开始把它们组合起来，形成一套系统化的工作方式。

---

## 三大核心功能

### CLAUDE.md = 工作手册

新员工入职时，你会给他一份手册：团队规范、代码风格、常见操作流程、注意事项。CLAUDE.md 就是给 AI 写的"入职手册"。每次 Claude Code 启动时，它会先读这个文件，了解项目的上下文和你的偏好。

好的 CLAUDE.md 应该包含：

- **项目结构说明**：文件在哪里、做什么用
- **代码风格要求**：用什么格式化工具（Formatter）、命名规范（Naming Convention）
- **常用命令**：如何运行（Run）、测试（Test）、部署（Deploy）
- **安全边界**：哪些操作可以自动做、哪些需要确认

一个常见的误区是把 CLAUDE.md 写得太长、太细。其实 AI 和人一样——信息太多反而抓不住重点。从最核心的几条规则开始，用着用着再慢慢补充，这样效果最好。

CLAUDE.md 可以放在多个位置，作用范围不同：

- 项目根目录的 `CLAUDE.md`：对整个项目生效
- 子目录的 `CLAUDE.md`：只对该目录下的工作生效
- 用户级别的 `~/.claude/CLAUDE.md`：对你所有项目生效（适合放个人偏好）

### Slash Commands = 标准操作规程（SOP）

想象一家连锁咖啡店的操作手册：制作拿铁有固定步骤、打扫有固定流程。Slash Commands 就是给 AI 定义的"标准操作规程"。

你把常见任务写成 Markdown 文件，放在 `.claude/commands/` 目录下，然后就可以用 `/命令名` 来触发。比如：

- `/test` —— 运行测试套件，分析失败的测试
- `/docs-sync` —— 同步文档和代码的一致性
- `/review` —— 按照团队标准审查代码

每个命令文件就是一个 Markdown 文件，里面写清楚你希望 AI 做什么。你还可以用 `$ARGUMENTS` 占位符来接收参数，让命令更灵活。

这个功能的核心价值是"复用"。你花 10 分钟写一个命令，以后每次用只需要 3 秒钟敲一个斜杠命令。而且团队共享这些命令后，每个人都能用同样的标准流程工作。

### SubAgents = 团队分工

一个人做所有事效率低，不如分工合作：一个人写代码、一个人写测试、一个人做文档审查。SubAgents（子代理）就是给 AI 做"分工"——主代理可以启动多个子代理，每个子代理有自己的角色和任务。

比如你让 Claude Code 做一个大的重构任务，它可以：

1. 启动一个子代理去分析现有代码结构
2. 启动另一个子代理去写测试
3. 自己负责整合结果和做最终决策

SubAgents 是三个功能中最高阶的。如果你是刚开始接触 Claude Code，不用急着学这个，先把 CLAUDE.md 和 Slash Commands 用好就已经很厉害了。

---

## 任务导读

原课程把任务分成两个部分：

### Part I: 构建自动化

从下面三类中选择 2 个以上来实现：

**A) 创建 Slash Commands**

设计可复用的自动化命令。建议从你日常开发中最频繁的操作入手：

- 你每天重复做的事情是什么？
- 哪些操作步骤固定、但每次都要手动打一堆指令？
- 有没有团队规范需要反复检查的？

这些就是 Slash Commands 的最佳候选。

**B) 编写 CLAUDE.md**

为你的项目编写 AI 工作指南。几个要点：

- 从项目最核心的信息开始（结构、技术栈、关键约束）
- 加上你最常见的操作命令（怎么运行、怎么测试）
- 明确告诉 AI 什么可以自动做、什么要先问你

**C) 设计 SubAgents**

让多个 AI 角色协作完成一个复杂任务。这通常在 Slash Commands 里面用 `claude` 子进程来实现。

### Part II: 使用自动化来改进 Starter Application

用你在 Part I 建立的自动化工具，去改进 Week 2 的应用（或者任何你手头的项目）。这一步的目的是验证你的自动化是否真正有用——不是为了交作业而做，而是要解决实际问题。

---

## 实际建议

如果你不确定从哪里开始，这里有一个推荐路径：

1. **先从 CLAUDE.md 开始**（类型 B）。这是最直接、最有用的。打开你正在做的项目，写一份 CLAUDE.md，然后观察 Claude Code 的行为变化。

2. **然后尝试 Slash Commands**（类型 A）。想想你反复做的操作，把它变成一个命令。从最简单的开始——哪怕只是"运行测试并总结结果"也是一个好的起步。

3. **最后挑战 SubAgents**（类型 C）。这个需要对前两个功能比较熟悉后再做。一个好的起步点是让一个子代理专门负责代码审查，另一个负责写测试。

不要追求完美。先做一个粗糙但能用的版本，用起来之后再迭代。

---

## 与主题线的连接

> 这周是从 Vibe Coding 到 Human-Agent Engineering（人机协作工程）的关键转折。Vibe Coding 是"随便让 AI 写代码看看行不行"；而这周学的方法论是"系统化地配置 AI，让它按照你的标准和流程工作"。区别就像一个人随手做饭 vs. 一家餐厅的标准化厨房管理。

想想看：

- CLAUDE.md 解决的是"上下文"问题——AI 不知道你的项目规范，你就得每次重复说
- Slash Commands 解决的是"复用"问题——同样的操作不需要每次都从头描述
- SubAgents 解决的是"复杂度"问题——大任务拆成小任务，各司其职

这三样东西组合在一起，就构成了一套完整的"AI 协作操作系统"。

---

## 环境准备

### 1. 启动 Starter Application

1. 激活 conda 环境：
   ```bash
   conda activate cs146s
   ```
2. （可选）安装 pre-commit hooks：
   ```bash
   pre-commit install
   ```
3. 从 `week4/` 目录运行应用：
   ```bash
   make run
   ```
4. 打开 http://localhost:8000 查看前端，http://localhost:8000/docs 查看 API 文档
5. 体验应用的当前功能，了解它能做什么

### 2. 安装 Claude Code

确保已安装 Claude Code CLI。这是本周练习的核心工具。

### 3. 了解应用结构

```
week4/
  backend/          # FastAPI 应用（路由、模型、服务）
  frontend/         # 静态前端（由 FastAPI 提供服务）
  data/             # SQLite 数据库和种子数据（seed data）
  docs/             # 任务列表（TASKS.md）
```

### 4. 常用命令

```bash
make test      # 运行测试
make format    # 格式化代码
make lint      # 代码检查
```

---

## 练习任务

### Part I：构建自动化（从以下三类中选 2 个或更多）

#### A) 自定义 Slash Commands

在 `.claude/commands/` 目录下创建 Markdown 文件，定义可复用的自动化命令。Claude Code 会通过 `/命令名` 暴露这些命令。

**示例 1：测试运行器**
- 文件名：`tests.md`
- 功能：运行 `pytest -q backend/tests --maxfail=1 -x`，如果通过则运行覆盖率检查（coverage）
- 输入：可选的标记（marker）或路径（path）
- 输出：失败摘要和下一步建议

**示例 2：文档同步**
- 文件名：`docs-sync.md`
- 功能：读取 `/openapi.json`，更新 `docs/API.md`，列出路由变化（route deltas）
- 输出：差异摘要（diff summary）和待办事项

**示例 3：重构工具**
- 文件名：`refactor-module.md`
- 功能：重命名模块（如 `services/extract.py` 改为 `services/parser.py`），更新导入（imports），运行 lint/测试
- 输出：修改文件清单和验证步骤

> 建议：保持命令聚焦，使用 `$ARGUMENTS` 传参，优先使用幂等步骤（idempotent steps）。

#### B) CLAUDE.md 指导文件

在仓库根目录（或 `week4/` 子目录）创建 `CLAUDE.md`，引导 Claude 的行为。

**可以包含的内容：**
- 代码导航和入口点：如何运行应用、路由位置（`backend/app/routers`）、测试位置、数据库种子数据
- 风格和安全边界：工具要求（black/ruff）、安全命令、禁止命令、lint/测试关卡（gates）
- 工作流模板："添加端点时，先写失败测试（failing test），再实现，最后运行 pre-commit"

> 建议：像迭代 Prompt 一样迭代 CLAUDE.md，保持简洁可执行。

#### C) SubAgents（角色专业化）

设计 2 个或更多协作的子代理（SubAgent），各负责一个工作流步骤。通常在 Slash Commands 里用 `claude` 子进程来实现。

**示例 1：TestAgent + CodeAgent**
- 流程：TestAgent 编写测试 -> CodeAgent 实现代码 -> TestAgent 验证

**示例 2：DocsAgent + CodeAgent**
- 流程：CodeAgent 添加路由 -> DocsAgent 更新文档并检查 OpenAPI 一致性

**示例 3：DBAgent + RefactorAgent**
- 流程：DBAgent 提出 Schema 变更 -> RefactorAgent 更新模型/路由/lint

> 建议：使用检查清单（checklist），角色间用 `/clear` 重置上下文，独立任务可并行。

### Part II：使用你的自动化

用你在 Part I 构建的自动化来改进 starter application。记录每个自动化的使用过程和效果，写入 `writeup.md` 或 `writeup-zh.md`。

---

## 推荐学习资源

- Claude Code 最佳实践: [anthropic.com/engineering/claude-code-best-practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- SubAgents 文档: [docs.anthropic.com/en/docs/claude-code/sub-agents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)

---

## 自检清单

- [ ] 创建了一个有效的 CLAUDE.md 文件
- [ ] 至少实现了 2 个自动化（Slash Commands、CLAUDE.md、SubAgents 中任选）
- [ ] 能解释 CLAUDE.md、Slash Commands、SubAgents 各自的用途
- [ ] 用自动化真正改进了一个工作流程
- [ ] 理解"配置 AI"和"使用 AI"的区别

---

[开始 Week 5 →](../week5/README.md)
