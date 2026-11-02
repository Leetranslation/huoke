# YxAgent · AI 外贸获客 Agent 平台

> 面向 B2B 外贸场景的 AI SDR：从「找客户」到「客户回复后自动停跟」的全链路自动化。

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3-42b883)](https://vuejs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791)](https://www.postgresql.org/)
[![Celery](https://img.shields.io/badge/Celery-5.4-37814A)](https://docs.celeryq.dev/)

---

## 这个项目解决什么问题

外贸业务员做客户开发的流程是：找目标客户 → 判断是不是真买家 → 找决策人邮箱 → 写个性化开发信 → 跟进 → 等回复。

这条路每一步都是体力活，而且**最难的不是写信，是判断**：
- 搜出来的是公司还是行业文章？
- 这家是买家还是同行？
- 客户回了一句「不好意思不需要」，还要不要继续发？

本项目把这条链路做成 Agent 流水线，把「判断」交给 LLM，把「执行」交给 Celery。

---

## 核心流水线

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ ① 线索发现  │ → │ ② 画像评分  │ → │ ③ 开发信    │ → │ ④ 追踪发送  │
│ Tavily 搜索 │   │ LLM 打分    │   │ LLM 生成    │   │ 像素+链接   │
│ LLM 实体清洗│   │ 需求信号    │   │ 人工审核    │   │ SMTP 投递   │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
                                                              ↓
                                                    ┌─────────────────┐
                                                    │ ⑤ 回复闭环      │
                                                    │ IMAP 收信       │
                                                    │ LLM 意图识别    │
                                                    │ 正向→跟进       │
                                                    │ 拒绝→终止       │
                                                    └─────────────────┘
```

---

## AI 落点（6 处，不是套壳）

| # | 场景 | 做法 | 为什么必须用 LLM |
|---|---|---|---|
| 1 | **企业 DNA 分析** | 抓官网 → 提取核心产品 / 目标客户类型 / 同行排除规则 | 客户类型定义是语义问题，规则写不出来（"用膜的人" vs "卖膜的人"） |
| 2 | **线索实体清洗** | 搜索结果 → 判断"这网页是不是一家企业" → 提取规范公司名 | 搜索引擎给的是网页标题（"Oil and Gas Companies"），要还原成公司实体 |
| 3 | **买家身份判定** | 判定 buyer / competitor / irrelevant / unknown | 关键判断："它用我的产品，还是卖/造我的产品" |
| 4 | **画像评分** | 业务描述 + 需求信号 + 匹配理由 + 0~100 分 | 要从非结构化网页内容里读出采购意向 |
| 5 | **开发信生成** | 基于画像 + 联系人职位生成个性化邮件 | 冷邮件转化率取决于个性化，模板信必死 |
| 6 | **回复意图识别** | positive / negative / neutral | 决定是继续跟进还是永久停止，误判会骚扰明确拒绝的客户 |

**关键取舍**：不做微调。B2B 获客的瓶颈是业务上下文（客户类型、排除规则）而非模型能力，Prompt + few-shot + 结构化输出足够。

---

## 技术栈

| 层 | 选型 | 说明 |
|---|---|---|
| 接入 | FastAPI + Pydantic v2 | 26 个 REST 接口，OpenAPI 自动文档 |
| AI 编排 | LangGraph | 跟进状态机（send / wait / stop 决策图） |
| 模型 | OpenAI 兼容，默认 DeepSeek | 换 Qwen / GLM 只改 3 个环境变量 |
| 数据 | PostgreSQL 16 + SQLAlchemy 2.0 + Alembic | 7 张表 |
| 异步 | Celery + Redis | 定时扫描跟进、定时收信 |
| 邮件 | SMTP（发）+ IMAP（收） | 发送与收信解耦，可换 SendGrid / SES |
| 前端 | Vue 3 + Vite + 自写 design system | 9 个页面，无 UI 框架依赖 |
| 部署 | Docker Compose | api + worker + beat + db + redis 一键起 |

---

## 架构分层

```
app/
├── api/          接入层：路由 + 依赖注入（8 个模块）
├── services/     业务层：编排用例（发送、画像、DNA、跟进）9 个
├── agent/        AI 层：LLM 封装 + Prompt + LangGraph 状态机 9 个
├── datasources/  数据源：Tavily / Europages / CSV / 邮箱提取，可插拔 10 个
├── senders/      发送端：Mock + SMTP 双实现，可插拔 4 个
├── models/       ORM 模型（7 张表）
├── repositories/ 数据访问
├── schemas/      Pydantic 请求/响应模型
├── tasks/        Celery 任务（跟进扫描、收信）
└── core/         配置 / DB / Redis / 安全
```

**设计原则**：业务层不依赖具体数据源和发送通道。换搜索引擎只加一个 `DataSource` 子类，换邮件服务只加一个 `EmailSender` 实现。

---

## 快速开始

### 方式一：Docker（推荐）

```bash
# 1. 配置
cp .env.example .env
# 填入 LLM_API_KEY、TAVILY_API_KEY、SMTP_*（见下表）

# 2. 启动全部服务
docker compose up -d

# 3. 初始化数据库
docker compose exec api alembic upgrade head

# 4. 访问
# 前端  http://localhost:5173
# 接口文档 http://localhost:8001/docs
```

### 方式二：本地开发

```bash
# 后端
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8001

# 前端
cd frontend && npm install && npm run dev

# 异步任务（另开两个终端）
uv run celery -A app.core.celery_app worker --loglevel=info --pool=solo
uv run celery -A app.core.celery_app beat --loglevel=info
```

### 必需的环境变量

| 变量 | 用途 | 获取方式 |
|---|---|---|
| `LLM_API_KEY` | 大模型调用 | [DeepSeek 开放平台](https://platform.deepseek.com/) |
| `TAVILY_API_KEY` | 线索搜索 | [Tavily](https://tavily.com/)（免费 1000 次/月） |
| `SMTP_HOST/USER/PASSWORD` | 发信 | 邮箱设置里开 SMTP 拿授权码 |
| `IMAP_*` | 收信（复用 SMTP 账号） | 同上，需额外开 IMAP 服务 |
| `PUBLIC_BASE_URL` | 邮件追踪像素的公网地址 | 本地测试用内网穿透，线上填域名 |
| `FOLLOW_UP_INTERVAL_DAYS` | 跟进间隔天数（默认 4） | 可选，按业务节奏调 |
| `FOLLOW_UP_MAX_STEPS` | 最多跟进轮次（默认 5） | 可选，防止过度骚扰 |

---

## 测试

```bash
uv run pytest
# 50 passed in ~5s
```

单元测试覆盖核心判断逻辑（全部离线，不调 LLM / 不连数据库）：

| 测试文件 | 覆盖内容 | 用例数 |
|---|---|---|
| `test_followup_graph.py` | 跟进状态机决策（首封 / 间隔等待 / 达上限 / 终止态） | 13 |
| `test_send_rules.py` | 发送前三道停止规则（未批准 / 重复发送 / 客户终止） | 10 |
| `test_filters.py` | 线索过滤（新闻/机构/栏目页）+ 邮箱分级（HR/学校剔除） | 12 |
| `test_entity_parse.py` | LLM 输出解析（裸 JSON / 带围栏 / 混杂文本）+ 域名推断公司名 | 15 |

`tests/` 下的其它文件是手工验证脚本（`diag_*` / `e2e_*`），不参与 pytest 收集。

---

## 评测结果

用 40 条人工标注样本评测两个核心判断（`python -m tests.eval_quality`）：

| 评测项 | 样本 | 准确率 | 说明 |
|---|---|---|---|
| **回复意图识别** | 20 条（8 正向 / 8 拒绝 / 4 中性） | **100%** | 中英混杂，含口语化拒绝（"别发了，烦不烦"） |
| **买家身份判定** | 20 家（8 买家 / 6 同行 / 6 无关） | **90%** | 2 例误判源于业务双重属性，见下 |

**两处误判分析**（重要，说明边界而非模型缺陷）：

| 公司 | 标注 | 预测 | 原因 |
|---|---|---|---|
| Bosch Rexroth Assembly Plant | buyer | competitor | 博世力士乐既造液压元件也做系统集成，买卖双重属性 |
| Schaeffler Hydraulics Division | buyer | competitor | 舍弗勒同时生产液压执行元件，业务边界模糊 |

这类"既买又卖"的企业，单靠公司名 + 摘要无法判断，实际业务中需要人工复核——这也是为什么**发送前必须人工审核**。

**评测局限**：样本由项目作者构造，非公开数据集；真实分布下准确率会有波动。

---

## 关键设计决策

**1. 不用「是否打开邮件」做跟进决策**
打开追踪依赖图片加载，客户端屏蔽图片、代理预取都会失真。跟进只看「距上次发送天数 + 是否回复」。

**2. 发送前必须人工审核**
AI 生成的邮件进入 `draft → pending_approval → approved → sent` 状态机，人批准才发。冷邮件发错成本太高。

**3. 邮件状态与客户生命周期分离**
- `emails.status`：单封邮件的流转（草稿/待审/已批/已发/失败）
- `contacts.status`：客户在漏斗里的位置（待触达/跟进中/已回复/已终止）

**4. 拒绝即终止**
客户回复「不要再发了」→ LLM 判 negative → `contacts.status = unsubscribed` → 停跟任务永久跳过。不做「再试一次」。

**5. 测试客户自动注入**
每个获客任务自动带一个测试客户（邮箱可配），用于验证追踪链路，不污染真实客户。

---

## 数据模型（7 表）

```
users ──< campaigns ──< companies ──< contacts ──< emails ──< email_events
                            │                        │
                            └──< follow_up_steps ────┘
```

- 客户生命周期挂在 `contacts.status`，不单独建关联表
- 邮件追踪事件（open / click / reply）统一存 `email_events`，`meta` 存回复正文
- 画像与 DNA 用 JSONB 存，避免频繁改表

---

## 已实现的功能

- [x] 企业 DNA 分析（官网 → 产品 / 客户类型 / 排除规则）
- [x] 线索发现（Tavily 搜索 + LLM 实体清洗 + 身份判定）
- [x] CSV 线索导入
- [x] 画像评分（业务描述 / 需求信号 / 匹配理由 / 分数）
- [x] 联系人提取（官网爬取 + 搜索引擎）
- [x] 开发信生成（基于画像 + 职位个性化）
- [x] 邮件审核流（草稿 → 待审 → 批准 → 发送）
- [x] 打开 / 点击追踪（像素 + 302 跳转）
- [x] IMAP 收信 + 回复意图识别
- [x] 自动跟进（Celery 每日扫描 + LangGraph 状态机）
- [x] 前端 9 页（工作台 / 任务 / 客户池 / 公司画像 / 邮件中心 / 跟进看板）

## 已知限制

| 限制 | 原因 | 上线方案 |
|---|---|---|
| 无多租户 | 单用户演示项目 | 加 `user_id` 隔离 + JWT 鉴权 |
| 追踪像素依赖临时隧道 | 本地无固定公网 IP | 部署后填域名 |
| 无数据导出 | 未实现 | 加 CSV 导出接口 |
| 免费搜索额度有限 | Tavily 1000 次/月 | 换 Serper / Bing API 或付费档 |

---

## 目录速览

```
YXAgent/
├── app/                  后端（分层见上）
├── alembic/              数据库迁移
├── frontend/             Vue 3 前端
├── data/                 CSV 示例数据
├── docs/                 设计文档
├── tests/                测试与调试脚本
├── docker-compose.yml    全栈编排
├── Dockerfile
└── pyproject.toml
```
