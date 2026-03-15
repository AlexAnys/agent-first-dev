> [← 返回首页](../README.md) · [指南目录](README.md) · [术语表](../TERMINOLOGY.md)

# 国内部署替代方案

本课程中提到的部分服务（如 Vercel、Cloudflare、Heroku 等）在国内可能存在访问不稳定或无法使用的情况。本指南提供国内可用的替代方案，帮助你顺利完成课程项目的开发和部署。

## 云平台

| 用途 | 课程推荐 | 国内替代 |
|------|----------|----------|
| 静态网站托管（Static Hosting） | Vercel, Netlify | 腾讯云 Webify, 阿里云 OSS 静态托管, Cloudflare Pages（可用但速度不稳定） |
| 后端服务部署（Backend Deployment） | Heroku, Railway | 腾讯云 SCF（云函数）, 阿里云 FC, 华为云 FunctionGraph |
| 容器化部署（Container Deployment） | AWS ECS, GCP | 腾讯云容器服务, 阿里云 ACK |
| 数据库（Database） | Supabase, PlanetScale | 腾讯云 TDSQL, 阿里云 RDS, 本地 SQLite 即可满足学习需求 |

## AI 服务

| 用途 | 课程使用 | 国内替代 |
|------|----------|----------|
| LLM API | OpenAI API | 智谱 AI（GLM）, 百度文心, 阿里通义千问, DeepSeek |
| 本地模型（Local Models） | Ollama（课程推荐） | Ollama 在国内可用，推荐继续使用 |
| AI 编码助手（AI Coding Assistant） | Cursor, GitHub Copilot | Cursor（可用）, Trae（字节）, 通义灵码 |

## 开发工具

| 用途 | 课程使用 | 国内可用性 |
|------|----------|-----------|
| GitHub | 代码托管 | 可用，但速度可能慢。替代：Gitee, 腾讯工蜂 |
| Ollama | 本地模型运行 | 可用 |
| Claude Code | 命令行 AI 工具 | 需要海外网络访问 |
| Warp Terminal | Week 5 | macOS 可用，需注意网络 |

## 建议

- 学习阶段优先使用本地方案（SQLite + Ollama + 本地服务器），减少对外部服务的依赖。
- 部署阶段根据实际需求选择平台，学习项目不需要复杂的云服务。
- 对于需要 LLM API 的练习，DeepSeek 和智谱 AI 提供性价比较高的 API 服务。
