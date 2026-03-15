> [← 本周导航](README.md) · [模块首页](../README.md) · [术语表](../../../TERMINOLOGY.md)

# Week 6 中文导读：安全扫描（Security Scanning）

## 这周在干什么

AI 能帮你快速写代码，但"快"不等于"安全"。这周你会学到：AI 生成的代码可能包含哪些安全漏洞（Vulnerability），以及如何用自动化工具来检测和修复它们。

这是整个课程中非常实用的一周。不管你将来用不用 AI 写代码，理解常见的安全问题都会让你成为更好的开发者。

---

## 为什么安全检查重要？

一个类比：AI 写代码就像一个非常高效但缺乏安全意识的实习生。他能快速完成任务，但可能会：

- **把密码直接写在代码里**（硬编码密钥，Hardcoded Secrets）
- **把用户输入直接拼进数据库查询**（SQL 注入，SQL Injection）
- **允许任何网站调用你的 API**（CORS 配置不当）
- **使用过时的加密算法**（比如 MD5）

这些问题在功能上可能完全正常——应用能跑，测试能过，用户能用。但在安全上是定时炸弹。一个 SQL 注入漏洞可能让攻击者读取你整个数据库的内容。

你可能会想："我只是在做练习项目，安全没那么重要吧？"问题是，不安全的编码习惯一旦养成，很难在"真正重要"的项目中突然改掉。现在就养成好习惯，将来省很多麻烦。

---

## Semgrep 是什么？

Semgrep 是一个代码扫描工具，类似代码的"安检机"。它用预定义的规则（Rules）扫描你的代码，找出常见的安全问题和代码质量问题。

和 lint 工具（比如 ESLint、pylint）不同的是，Semgrep 专注于安全相关的问题，而且支持多种编程语言。

### Semgrep 的三种扫描类型

理解这三种类型很重要，因为它们检测的问题完全不同：

**1. SAST（Static Application Security Testing，静态应用安全测试）**

直接分析你写的源代码，找出不安全的编码模式。比如：
- 你在代码里拼接 SQL 字符串 → 它会提醒你用参数化查询（Parameterized Query）
- 你用了不安全的函数 → 它会建议安全的替代方案

**2. Secrets（密钥检测）**

扫描代码中硬编码的敏感信息。比如：
- API Key 直接写在代码里
- 数据库密码出现在配置文件中
- AWS 访问密钥被提交到 Git

这类问题特别常见于 AI 生成的代码——因为 AI 在生成示例时，经常会"编造"一个看起来像真实密钥的字符串，而你可能没注意就直接用了。

**3. SCA（Software Composition Analysis，软件成分分析）**

检查你项目依赖的第三方包（比如 npm 包、pip 包）是否有已知的安全漏洞。这不是检查你的代码，而是检查你用的别人的代码。

比如你的 `requirements.txt` 里用了某个版本的 Flask，而这个版本有已知的安全漏洞，SCA 就会提醒你升级。

---

## 常见安全问题（本周可能遇到的）

### SQL 注入（SQL Injection）

不安全的写法：
```python
# 千万别这么写
query = f"SELECT * FROM users WHERE name = '{user_input}'"
```

如果 `user_input` 是 `'; DROP TABLE users; --`，你的整个用户表就没了。

安全的写法：
```python
# 用参数化查询
query = "SELECT * FROM users WHERE name = ?"
cursor.execute(query, (user_input,))
```

### 硬编码密钥（Hardcoded Secrets）

不安全的写法：
```python
API_KEY = "sk-1234567890abcdef"
```

安全的写法：
```python
import os
API_KEY = os.environ.get("API_KEY")
```

### 不安全的 CORS 配置

不安全的写法：
```python
# 允许所有来源访问——相当于把门完全打开
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

安全的写法：
```python
# 只允许特定的前端域名访问
app.add_middleware(CORSMiddleware, allow_origins=["https://myapp.com"])
```

### 弱加密（Weak Cryptography）

不安全的写法：
```python
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()
```

安全的写法：
```python
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

MD5 和 SHA1 在安全场景下已经不够用了。用 bcrypt、scrypt 或 argon2 来处理密码。

---

## 任务导读

原始作业（assignment.md）的核心流程是：

### 第一步：运行 Semgrep 扫描

按照 assignment.md 中提供的命令运行扫描。Semgrep 会输出一份报告，列出它发现的所有问题，包括：
- 问题描述
- 所在文件和行号
- 严重程度（severity）
- 建议的修复方式

### 第二步：选择 3 个问题修复

从扫描结果中挑 3 个你能理解的问题来修复。建议挑不同类型的问题（比如一个 SAST、一个 Secrets、一个 SCA），这样你的学习覆盖面更广。

### 第三步：记录修复过程

对每个修复，你需要说清楚三件事：
1. **问题是什么**：Semgrep 报了什么
2. **为什么危险**：这个问题在真实场景中可能造成什么后果
3. **你怎么修的**：具体改了什么代码

这个记录过程很重要——它迫使你理解问题的本质，而不是机械地按建议改代码。

---

## 与主题线的连接

Agentic Coding 不只是"让 AI 帮你写代码"，还包括"确保 AI 写的代码是安全的"。安全扫描应该成为你使用 AI 编码后的标准流程——就像飞行员起飞前的检查清单（Preflight Checklist）。

这也是 Vibe Coding 和专业开发的一个重要区别：专业开发者会检查 AI 的输出。不是因为不信任 AI，而是因为任何人（包括 AI）写的代码都应该经过安全检查。

在你的日常工作流中，可以考虑把 Semgrep 扫描加入到以下环节：
- 每次让 AI 生成代码后
- 每次提交代码前（可以用 pre-commit hook 自动化）
- 定期对整个项目进行全面扫描

---

## 自检清单

- [ ] 理解为什么 AI 生成的代码需要安全检查
- [ ] 成功运行了 Semgrep 扫描
- [ ] 修复了至少 3 个安全问题
- [ ] 能解释每个修复为什么能消除风险
- [ ] 理解 SAST、Secrets、SCA 三种扫描类型的区别

[开始 Week 7 →](../week7/)
