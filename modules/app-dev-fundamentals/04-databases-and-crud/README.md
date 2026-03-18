> [← 模块首页](../README.md) · [← 03: 请求的生命周期](../03-request-lifecycle/README.md) · [05: API →](../05-apis/README.md)

# 04: 数据库与 CRUD — 数据的四种基本操作

> 一句话：所有应用本质上都在做四件事——创建（Create）、读取（Read）、更新（Update）、删除（Delete）。

## 为什么 Coding Agent 用户需要懂这个

When you ask AI to "add a feature to save user preferences", you're asking it to implement Create and Update operations. Understanding CRUD helps you describe features precisely and verify AI's implementation.

## 核心心智模型

### CRUD = 所有应用的骨架

- **Create**: 用户注册、发帖、下单
- **Read**: 查看个人资料、浏览商品列表、搜索
- **Update**: 修改密码、编辑文章、更新订单状态
- **Delete**: 注销账户、删除评论

Every feature you can think of maps to one of these four operations.

### 数据库 = 电子表格

最简单的类比：数据库就是一个Excel。

- 数据库 = 整个 Excel 文件
- 表（Table）= 一个 Sheet
- 行（Row）= 一条记录
- 列（Column）= 一个字段
- 每行有唯一 ID（主键）

### 查询 = 提问

"给我所有状态为'待发货'的订单" = 一个查询（Query）

"这个月注册了多少用户？" = 一个聚合查询

查询就是向数据库提问，数据库返回符合条件的行。

### 外键：表与表之间的桥梁

文章表里有一个 user_id 列 → 这就是外键

它的意思是："这篇文章属于 ID 为 X 的用户"

外键把 02 数据建模中设计的关系变成了数据库中的现实

## 常见误区

1. "数据库很复杂" — 心智模型就是电子表格，操作就是 CRUD
2. "删除就是真删除" — 很多应用用"软删除"（加一个 deleted 标记），数据还在
3. "AI 会自动处理数据关系" — AI 需要你告诉它表之间怎么关联（外键）

## 这个概念在 Agentic Coding 中的应用

当你描述需求时，用 CRUD 语言："用户可以 Create 新的笔记，Read 自己的笔记列表，Update 笔记内容，Delete 不需要的笔记"。这比"做一个笔记功能"精确得多。

Link to Agentic Coding Week 2 (全栈开发中会实际操作数据库)

## 下一步

→ 05: API — 一切都是 HTTP 请求
