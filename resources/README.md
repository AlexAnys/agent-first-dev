> [← 返回首页](../README.md) · [模块首页](../modules/agentic-coding/README.md) · [术语表](../TERMINOLOGY.md)

# 学习资源

按主题组织的推荐阅读列表，涵盖 10 周课程中提到的所有资源。每条资源标注关联周次，方便交叉引用。

---

## 提示工程与 LLM 基础

| 资源 | 类型 | 关联周次 | 说明 |
|------|------|----------|------|
| [Deep Dive into LLMs](https://www.youtube.com/watch?v=7xTGNNLPyMI) | 视频 | Week 1 | Karpathy 的 LLM 深度讲解（约 3.5 小时，建议至少看前 30 分钟） |
| [Prompt Engineering Overview](https://cloud.google.com/discover/what-is-prompt-engineering) | 文章 | Week 1 | Google 的提示工程系统概览 |
| [Prompt Engineering Guide](https://www.promptingguide.ai/techniques) | 指南 | Week 1 | 系统化的提示工程技术指南 |
| [AI Prompt Engineering: A Deep Dive](https://www.youtube.com/watch?v=T9aRN5JkmL8) | 视频 | Week 1 | 提示工程深度讲解 |

## AI 辅助开发

| 资源 | 类型 | 关联周次 | 说明 |
|------|------|----------|------|
| [Specs Are the New Source Code](https://blog.ravi-mehta.com/p/specs-are-the-new-source-code) | 文章 | Week 2 | "规范是新的源代码"，理解 AI 时代的开发思维转变 |
| [Writing Effective Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents) | 文章 | Week 2 | Anthropic 官方指南：如何为 AI 设计有效的工具接口 |
| [How Long Contexts Fail](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html) | 文章 | Week 2 | 长上下文的失败模式分析 |
| [Advanced Context Engineering for Coding Agents](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md) | 指南 | Week 2 | 高级上下文工程实践指南 |
| [How OpenAI Uses Codex](https://cdn.openai.com/pdf/6a2631dc-783e-479b-b1a4-af0cfbd38630/how-openai-uses-codex.pdf) | PDF | Week 1 | OpenAI 内部如何使用 Codex 的技术报告 |
| [How Anthropic Uses Claude Code](https://www-cdn.anthropic.com/58284b19e702b49db9302d5b6f135ad8871e7658.pdf) | PDF | Week 4 | Anthropic 内部如何使用 Claude Code |
| [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) | 文章 | Week 4 | 官方最佳实践指南 |
| [Good Context Good Code](https://blog.stockapp.com/good-context-good-code/) | 文章 | Week 4 | StockApp 团队通过上下文管理提升 2.5x 生产力的案例 |
| [Peeking Under the Hood of Claude Code](https://medium.com/@outsightai/peeking-under-the-hood-of-claude-code-70f5a94a9a62) | 文章 | Week 4 | Claude Code 内部工作原理分析 |
| [Awesome Claude Agents](https://github.com/vijaythecoder/awesome-claude-agents) | 代码 | Week 4 | Claude Code 代理模式的社区资源集 |
| [Super Claude Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework) | 代码 | Week 4 | 增强 Claude Code 能力的开源框架 |
| [How Warp Uses Warp to Build Warp](https://notion.warp.dev/How-Warp-uses-Warp-to-build-Warp-21643263616d81a6b9e3e63fd8a7380c) | 文章 | Week 5 | Warp 团队自己如何使用 Warp 进行开发 |
| [Context Rot Research](https://research.trychroma.com/context-rot) | 研究 | Week 6 | 上下文衰减对 AI 输出质量的影响研究 |

## MCP 与工具生态

| 资源 | 类型 | 关联周次 | 说明 |
|------|------|----------|------|
| [MCP Introduction](https://stytch.com/blog/model-context-protocol-introduction/) | 文章 | Week 3 | MCP 协议入门：什么是 Model Context Protocol |
| [APIs Don't Make Good MCP Tools](https://www.reillywood.com/blog/apis-dont-make-good-mcp-tools/) | 文章 | Week 3 | 为什么不能简单地把 API 包装成 MCP 工具 |
| [MCP Server Examples](https://github.com/modelcontextprotocol/servers) | 代码 | Week 3 | 官方 MCP 服务器示例集 |
| [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) | 代码 | Week 3 | MCP 的 TypeScript 开发套件 |
| [Cloudflare MCP Server Authentication](https://developers.cloudflare.com/agents/guides/remote-mcp-server/#add-authentication) | 文档 | Week 3 | Cloudflare 上的 MCP 认证指南 |
| [Warp University](https://www.warp.dev/university) | 教程 | Week 5 | Warp 官方教程平台 |
| [Warp vs Claude Code](https://www.warp.dev/university/getting-started/warp-vs-claude-code) | 文章 | Week 5 | 两个工具的定位和差异对比 |

## 安全

| 资源 | 类型 | 关联周次 | 说明 |
|------|------|----------|------|
| [OWASP Top Ten](https://owasp.org/www-project-top-ten/) | 文档 | Week 6 | Web 安全十大风险类型，安全入门必读 |
| [GitHub Copilot RCE via Prompt Injection](https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection/) | 文章 | Week 6 | Copilot 被提示注入攻击的真实案例 |
| [Finding Vulnerabilities with Claude Code &amp; Codex](https://semgrep.dev/blog/2025/finding-vulnerabilities-in-modern-web-apps-using-claude-code-and-openai-codex/) | 文章 | Week 6 | Semgrep 用 AI 在开源项目中发现 46 个真实漏洞 |
| [SAST vs DAST](https://www.splunk.com/en_us/blog/learn/sast-vs-dast.html) | 文章 | Week 6 | 静态分析与动态分析的对比 |
| [Agentic AI Threats](https://unit42.paloaltonetworks.com/agentic-ai-threats/) | 文章 | Week 6 | Palo Alto Unit 42 对 AI 代理安全威胁的分析 |

## 代码审查与质量

| 资源 | 类型 | 关联周次 | 说明 |
|------|------|----------|------|
| [Code Reviews: Just Do It](https://blog.codinghorror.com/code-reviews-just-do-it/) | 文章 | Week 7 | 为什么代码审查如此重要（经典文章） |
| [How to Review Code Effectively](https://github.blog/developer-skills/github/how-to-review-code-effectively-a-github-staff-engineers-philosophy/) | 文章 | Week 7 | GitHub Staff Engineer 的代码审查方法论 |
| [Lessons from a Million AI Code Reviews](https://www.youtube.com/watch?v=TswQeKftnaw) | 视频 | Week 7 | Graphite CPO 分享 AI 审查经验 |
| [AI-Assisted Assessment in Modern Code Review](https://arxiv.org/pdf/2405.13565) | 论文 | Week 7 | 学术论文：AI 辅助代码审查的系统评估 |
| [AI Code Review Best Practices](https://graphite.dev/guides/ai-code-review-implementation-best-practices) | 文章 | Week 7 | Graphite 的 AI 代码审查实践指南 |
| [Code Review Essentials](https://blakesmith.me/2015/02/09/code-review-essentials-for-software-teams.html) | 文章 | Week 7 | 代码审查基础：团队协作的核心实践 |

## 监控与运维

| 资源 | 类型 | 关联周次 | 说明 |
|------|------|----------|------|
| [Introduction to Site Reliability Engineering](https://sre.google/sre-book/introduction/) | 文档 | Week 9 | Google SRE Book 入门章节 |
| [Observability Basics You Should Know](https://www.splunk.com/en_us/blog/learn/observability.html) | 文章 | Week 9 | 可观测性基础概念 |
| [Kubernetes Troubleshooting with AI](https://www.resolveai.io/blog/kubernetes-troubleshooting-with-ai) | 文章 | Week 9 | 用 AI 诊断 Kubernetes 问题 |
| [Your New Autonomous Teammate](https://www.resolveai.io/blog/your-new-autonomous-teammate) | 文章 | Week 9 | Resolve AI 的自主代理理念 |
| [Role of Multi Agent Systems in Making Engineers AI-native](https://www.resolveai.io/blog/role-of-multi-agent-systems-in-making-engineers-ai-native) | 文章 | Week 9 | 多代理系统在工程团队中的角色 |
| [Benefits of Agentic AI in On-call Engineering](https://www.resolveai.io/blog/benefits-of-agentic-ai-in-on-call-engineering) | 文章 | Week 9 | AI 代理在 On-call 工程中的价值 |

## 多技术栈与应用生成

| 资源 | 类型 | 关联周次 | 说明 |
|------|------|----------|------|
| [Vercel v0](https://v0.dev/) | 工具 | Week 8 | Vercel 的 AI UI 生成平台 |

---

## 课程嘉宾

| 周次 | 嘉宾 | 身份 | 主题 |
|------|------|------|------|
| Week 3 | Silas Alberti | Cognition（Devin）研究负责人 | AI IDE |
| Week 4 | Boris Cherney | Anthropic, Claude Code 创建者 | Coding Agent Patterns |
| Week 5 | Zach Lloyd | Warp CEO | The Modern Terminal |
| Week 6 | Isaac Evans | Semgrep CEO | AI Testing and Security |
| Week 7 | Tomas Reimers | Graphite CPO | Modern Software Support |
| Week 8 | Gaspar Garcia | Vercel AI 研究负责人 | Automated UI and App Building |
| Week 9 | Mayank Agarwal & Milind Ganjoo | Resolve AI CTO & Technical Staff | Monitoring and Incident Response |
| Week 10 | Martin Casado | a16z 合伙人 | The Future of AI Software Engineering |
