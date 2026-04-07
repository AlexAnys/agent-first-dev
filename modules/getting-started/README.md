> [← 返回首页](../../README.md) · [术语表](../../TERMINOLOGY.md)

# Getting Started — 从零开始的 30 分钟

> 从完全没写过代码，到用 AI 做出一个能跑的网页。本指南帮你在 30 分钟内完成环境搭建和第一个项目。

## 你需要准备什么

- 一台电脑（Mac、Windows 或 Linux 都可以）
- 一个浏览器（推荐 Chrome）
- 一个 GitHub 账号（免费注册：[github.com](https://github.com)）
- 愿意尝试新东西的心态

**不需要**：编程经验、计算机科学背景、任何付费软件。

## 第一步：选择你的 AI 编码工具

你需要一个 AI 编码工具来开始。以下是推荐方案：

### 方案 A：Cursor（推荐新手）

[Cursor](https://cursor.com) 是一个内置 AI 的代码编辑器，界面友好，适合第一次接触代码的人。

1. 访问 [cursor.com](https://cursor.com)，下载并安装
2. 打开 Cursor，用 GitHub 账号登录
3. 免费版包含 AI 对话功能，足够开始学习

### 方案 B：Claude Code（推荐有一定经验后使用）

[Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) 是 Anthropic 的命令行 AI 编码工具，更强大但需要终端操作。

1. 需要 Anthropic API key（[console.anthropic.com](https://console.anthropic.com)）
2. 安装方式：在终端运行 `npm install -g @anthropic-ai/claude-code`
3. 适合完成 Week 1-2 后再使用，Week 4 会深入学习

### 方案 C：零安装方案（GitHub Codespaces）

如果你不想在本地安装任何东西：

1. 打开任意 GitHub 仓库（比如 [github.com/new](https://github.com/new) 创建一个新仓库）
2. 按键盘上的 `.` 键 → 自动打开浏览器版 VS Code
3. 或者在仓库页面点击绿色 "Code" 按钮 → "Codespaces" → "Create codespace"
4. 完全在浏览器里写代码，不需要安装任何东西

> **不确定选哪个？** 如果你是第一次接触代码，用 **Cursor**。如果你连软件都不想装，用 **GitHub Codespaces**。

## 第二步：认识终端（3 分钟）

终端（Terminal）是你和电脑对话的文字界面。别被它吓到——你只需要会三个命令：

- **打开终端**：
  - Mac：按 `Cmd+空格`，输入 "Terminal"，回车
  - Windows：按 `Win+R`，输入 "cmd"，回车
  - Cursor/Codespaces：编辑器底部就有内置终端

- **三个够用的命令**：
  ```
  ls          → 看当前目录有什么文件（Windows 用 dir）
  cd 文件夹名  → 进入某个文件夹
  cd ..       → 返回上一级
  ```

> 这三个命令够你用很久了。遇到更复杂的操作？问 AI。

## 第三步：你的第一个项目（15 分钟）

我们来做一个真实的东西——一个个人链接页（类似 Linktree）。

### 3.1 创建项目

1. 打开 Cursor（或你选的工具）
2. 创建一个新文件夹，命名为 `my-first-page`
3. 在文件夹里创建一个文件 `index.html`

### 3.2 让 AI 帮你写

在 Cursor 的 AI 对话框（按 `Cmd+L` 或 `Ctrl+L`）里输入：

```
帮我创建一个个人链接页面（类似 Linktree），用纯 HTML 和 CSS。
要求：
- 顶部显示我的名字和一句话介绍
- 下面是 3-5 个链接按钮（GitHub、LinkedIn 等）
- 页面要好看，用现代简洁的设计风格
- 全部写在一个 index.html 文件里
```

AI 会帮你生成完整的代码。把代码复制到 `index.html` 文件里。

### 3.3 预览你的网页

- 在 Cursor 里：右键 `index.html` → "Open with Live Server"（如果有这个选项）
- 或者直接双击 `index.html` 文件，它会在浏览器里打开
- 你应该能看到一个漂亮的个人链接页面！

### 3.4 修改它

试试对 AI 说：
- "把背景色改成深色主题"
- "加一个头像圆形图片"
- "让按钮有鼠标悬停效果"

每次修改后刷新浏览器，看看变化。**这就是 AI 辅助开发的基本循环**：描述你想要的 → AI 生成代码 → 预览 → 继续迭代。

## 第四步：把它发布到互联网（10 分钟）

让全世界都能看到你的页面：

1. 在 GitHub 上创建一个新仓库（[github.com/new](https://github.com/new)），取名 `my-first-page`
2. 把你的 `index.html` 文件上传到仓库
3. 进入仓库 → Settings → Pages → Source 选 "main" 分支 → Save
4. 等 1-2 分钟，你的页面就上线了，地址是 `https://你的用户名.github.io/my-first-page`

**恭喜！你刚刚从零开始，用 AI 做出了一个真实的、全世界都能访问的网页。**

## 常见问题

### "我需要买 Claude Pro / Cursor Pro 吗？"
不需要。免费版足够完成所有学习内容。如果你开始大量使用，可以考虑付费，但不是必须。

### "学完这个指南需要多久？"
30 分钟到 1 小时，取决于你是否部署到 GitHub Pages。

### "我不懂英文，AI 工具都是英文界面怎么办？"
你可以用中文和 AI 对话。AI 完全理解中文指令。界面是英文的，但核心操作（对话、生成代码）都支持中文。

### "接下来学什么？"
你现在已经准备好了！根据你的情况选择：
- **想理解软件怎么运作** → [Application Development 模块](../app-dev-fundamentals/README.md)
- **想直接开始与 AI 协作开发** → [Agentic Coding Week 1](../agentic-coding/week1/README.md)

---

[← 返回首页](../../README.md) · [Agentic Coding →](../agentic-coding/README.md) · [Application Development →](../app-dev-fundamentals/README.md)
