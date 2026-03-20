> [← 模块首页](../README.md) · [← 上一章: 数据建模](../02-data-modeling/README.md) · [下一章: 数据库与 CRUD →](../04-databases-and-crud/README.md)

> 已经理解 MVC 或请求处理模式？可以直接跳到 [04: 数据库与 CRUD](../04-databases-and-crud/README.md)。

# 03: 请求的生命周期（RCAV 模式）

> 一句话：一个 URL 如何变成你看到的页面？四步：Route → Controller → Action → View。

> RCAV 和业界常说的 MVC（Model-View-Controller）本质相同，只是更明确地拆分了 Route 和 Action 两步。如果你在其他地方看到 MVC，知道是同一回事就行。

## 为什么 Coding Agent 用户需要懂这个

当你对 AI 说"加一个显示用户资料的页面"时，AI 实际上需要创建至少四样东西：一条路由规则、一个控制器、一个处理逻辑、一个页面模板。

如果你理解 RCAV 模式，你就能：

- **检查 AI 是不是四步都做了** — 有时候 AI 会漏掉某一步，比如定义了路由但忘了写视图
- **精准定位出错的位置** — 页面白屏？可能是路由没匹配上。页面出来了但数据为空？可能是 Action 里没查数据库。会看 RCAV 四步，就能快速缩小排查范围
- **用结构化语言下指令** — "在 `/dashboard` 路由的 `index` action 里查询当前用户的所有项目，传给 view 渲染"比"做一个仪表板"精确十倍

## 核心心智模型

### 一个类比：餐厅的完整点餐流程

在 [01 章](../01-how-the-web-works/README.md)我们讲了请求-响应的基本模型。现在我们展开来看请求到达服务器之后，内部具体发生了什么：

| 步骤 | 餐厅 | Web 应用 |
|------|------|----------|
| 1. 点菜 | 你说"我要宫保鸡丁" | 浏览器请求 `/dishes/kung-pao-chicken` |
| 2. 服务员查菜单 | 确认菜单上有这道菜，找到对应的厨师 | **Route**：URL 匹配路由规则，找到控制器 |
| 3. 对应的厨师 | 中餐厨师负责 | **Controller**：DishesController 处理 |
| 4. 具体做法 | 厨师按菜谱操作：切鸡肉、炒花生… | **Action**：`show` 方法查数据库、准备数据 |
| 5. 装盘上桌 | 把做好的菜装在盘子里端上来 | **View**：把数据渲染成 HTML 页面返回 |

### RCAV 四步详解

#### 第一步：Route（路由）

路由是 URL 和代码之间的"路标"。它定义了一条规则：当收到某个 URL 的请求时，交给哪个 Controller 的哪个 Action 去处理。

```
GET /users/123  →  UsersController#show
GET /articles   →  ArticlesController#index
POST /articles  →  ArticlesController#create
```

注意：同一个 URL（`/articles`）在不同的 HTTP 方法（GET vs POST）下可以指向不同的 Action。GET `/articles` 是"查看文章列表"，POST `/articles` 是"创建新文章"。

#### 第二步：Controller（控制器）

Controller 是一个"部门"，负责处理一类相关的请求。UsersController 处理所有和用户相关的请求，ArticlesController 处理所有和文章相关的请求。

一个 Controller 通常对应你数据模型里的一个名词（还记得 [02 章](../02-data-modeling/README.md) 的"名词变成表"吗？）。有 User 表，就通常有 UsersController。

#### 第三步：Action（动作）

Action 是 Controller 里的一个具体方法，是真正"干活"的地方。它做两件事：
1. 和数据库交互（查数据、存数据、改数据、删数据）
2. 把结果准备好，交给 View 去渲染

#### 第四步：View（视图）

View 是最终用户看到的东西。它拿到 Action 准备好的数据，渲染成 HTML（或者 JSON，一种数据格式，在 [05 章](../05-apis/README.md) 会详细介绍）返回给浏览器。

View 本身不做任何逻辑判断、不做数据库查询——它只负责"展示"。这是一个重要的职责分离原则。

### 标准的 7 个 Action

几乎所有 Web 框架都遵循同一套约定：对每个资源（名词），有 7 个标准的 Action：

| Action | HTTP 方法 | URL 示例 | 做什么 |
|--------|-----------|----------|--------|
| **index** | GET | `/articles` | 显示列表 |
| **show** | GET | `/articles/123` | 显示一条的详情 |
| **new** | GET | `/articles/new` | 显示"新建"表单 |
| **create** | POST | `/articles` | 保存新建的数据 |
| **edit** | GET | `/articles/123/edit` | 显示"编辑"表单 |
| **update** | PATCH/PUT | `/articles/123` | 保存修改的数据 |
| **destroy** | DELETE | `/articles/123` | 删除数据 |

这 7 个 Action 覆盖了大多数 Web 应用 **90% 以上的操作**。当你理解了这 7 个 Action，你就理解了几乎所有"增删改查"页面的工作方式。

你不需要背这 7 个 Action。先知道它们存在就够了——在实际开发中会自然记住。

更重要的是：当你让 AI"为文章加上编辑功能"时，AI 知道它需要加 `edit` action（显示表单）和 `update` action（保存修改）——两步，不是一步。如果你也知道这一点，你就能检查 AI 是否做完整了。

### RCAV 的完整图解

```
浏览器请求 GET /articles/123
        │
        ▼
    ┌──────────┐
    │  Route   │  匹配规则：GET /articles/:id → ArticlesController#show
    └────┬─────┘
         │
         ▼
    ┌──────────────────┐
    │  Controller      │  ArticlesController
    │  └─ Action: show │  article = 从数据库查 id=123 的文章
    └────┬─────────────┘
         │
         ▼
    ┌──────────┐
    │   View   │  把 article 的标题、内容渲染成 HTML
    └────┬─────┘
         │
         ▼
    浏览器收到 HTML，显示页面
```

## 常见误区

### 误区 1："每个页面都是独立的"

不是。每个页面都经过 RCAV 四步。看似独立的页面背后，共享着相同的模式。理解了一个页面的 RCAV，你就理解了所有页面的 RCAV。

### 误区 2："URL 就是文件路径"

在早期的静态网站中，`/about.html` 确实对应服务器上的一个文件。但在现代 Web 应用中，URL 是一条**路由规则**，它映射到代码逻辑，不映射到文件。`/users/123` 不是服务器上的某个文件夹，而是一个匹配规则，触发 UsersController 的 show action。

### 误区 3："前端框架改变了一切"

React、Vue 这些前端框架看起来打破了 RCAV 模式，但本质没变。它们只是把"View 渲染"从服务器搬到了浏览器端。请求-路由-数据处理-展示这四步依然存在，只是执行的位置变了。理解了 RCAV，你对前端框架的理解也会更快。

## 这个概念在 Agentic Coding 中的应用

RCAV 是和 AI 协作开发时最实用的"共同语言"之一：

- **描述需求时用 RCAV 的语言**："添加一个 `GET /dashboard` 路由，在 `DashboardController` 的 `index` action 里查询当前用户的所有项目，用 `dashboard/index` 视图渲染成卡片列表。" 这比"做一个仪表板页面"有效十倍。
- **Review AI 生成的代码时按 RCAV 检查**：路由定义了吗？Controller 存在吗？Action 里查了数据库吗？View 模板写了吗？四步都到位了，功能就不会缺失。
- **调试时按 RCAV 定位**：404 错误？大概率是 Route 的问题。500 错误？看 Action 里的代码。页面出来了但数据不对？看 Action 查询逻辑或 View 渲染逻辑。

## 动手试一试

### 练习 1：在真实网站中追踪 RCAV
1. 打开任意一个 Web 应用（比如 GitHub）
2. 点击不同的页面，观察 URL 的变化：
   - `github.com/AlexAnys` → 这是哪个 Controller 的哪个 Action？（Users#show）
   - `github.com/AlexAnys/agent-first-dev` → （Repositories#show）
   - `github.com/AlexAnys/agent-first-dev/issues` → （Issues#index）
   - `github.com/AlexAnys/agent-first-dev/issues/new` → （Issues#new）
3. 你会发现所有页面都符合 RCAV 模式——URL 决定了走哪条路由

### 练习 2：用 JSON Placeholder 体验 7 个标准 Action
打开 [JSONPlaceholder](https://jsonplaceholder.typicode.com/) — 一个免费的模拟 API：
- **index**（列表）：在浏览器打开 `https://jsonplaceholder.typicode.com/posts` → 看到所有文章
- **show**（详情）：打开 `https://jsonplaceholder.typicode.com/posts/1` → 看到第 1 篇文章
- **嵌套资源**：打开 `https://jsonplaceholder.typicode.com/posts/1/comments` → 看到第 1 篇文章的所有评论

注意 URL 的模式：`/资源名` = 列表，`/资源名/id` = 详情。这就是 RCAV 中的 Route 规则。

## 下一步

→ [04: 数据库与 CRUD](../04-databases-and-crud/README.md)

---

[← 上一章: 数据建模](../02-data-modeling/README.md) · [下一章: 数据库与 CRUD →](../04-databases-and-crud/README.md)
