# AI 外贸获客 Agent 平台 · 产品需求文档（PRD）

- 版本：v1.0
- 日期：2026-10-11
- 状态：讨论定稿

---

## 1. 产品概述

### 1.1 一句话定位

面向外贸 B2B 企业 / 销售团队的 AI 获客工具：输入「我的产品 / 官网」，自动找到海外潜在客户并个性化触达。

### 1.2 目标用户

- 外贸 SOHO（个人）
- 外贸初创 / 小微团队
- B2B 工业品、消费品出口企业

### 1.3 核心价值

把「找客户 → 发开发信 → 追踪跟进」整条链路自动化，替代人工找线索、写邮件、盯回复。

### 1.4 对标产品

- 国内：贸小七、麦穗获客
- 海外：Apollo.io、Instantly、Snov.io
- 赛道：AI 外拓获客 / AI SDR（outbound sales automation）

### 1.5 产品边界（明确不做）

- 只做邮件触达，不做 WhatsApp / 社媒 / 电话
- 只做 B2B，不做 B2C
- 只做「找客户 → 发开发信 → 追踪跟进」，不做完整 CRM、不做成交后环节

## 2. 用户角色与场景

### 2.1 角色

- 销售 / 业务员：建任务、挑客户、发信、跟进
- 管理员（团队版）：团队权限、客户资产沉淀

### 2.2 典型使用场景

1. 用户建获客任务（产品 / 官网 / 目标市场 / 关键词）
2. 系统采集线索，生成候选公司列表
3. 用户查看画像排序，挑高匹配客户入池
4. 系统生成个性化开发信
5. 发送 + 追踪（打开 / 点击）
6. 系统按状态机自动跟进，直到回复 / 拒绝

## 3. 完整功能清单

以四段流水线为骨架，AI 三落点为核。

### 第①段 · 线索采集
- 搜索引擎获客（关键词 → 公司 + 邮箱）
- 海关数据（HS 编码 → 采购商）
- 手动导入（CSV 种子客户）

### 第②段 · 画像匹配（AI 核心）
- LLM 结构化抽取：行业 / 规模 / 地区 / 需求信号
- 匹配度评分 + 排序（语义理解，非关键词规则）
- 决策人识别（CEO / Buyer）

### 第③段 · 个性化触达（AI 核心）
- 产品知识库（RAG 底座）
- 千邮千面生成 + A/B 多版本
- 邮件发送 + 打开 / 点击追踪 + 送达性

### 第④段 · 自动跟进（AI 核心 / Agent）
- LangGraph 状态机（未打开 / 打开未回 / 回复 / 拒绝）
- 意向判断 + 递进式跟进序列
- 销售漏斗

### 横向支撑
- 客户池（分级 / 标签 / 跟进记录）
- 账号 + 团队权限
- 数据统计看板

### 明确砍掉（避免跑偏）
LBS 地图、展会、领英、社媒运营、建站、企业邮箱——传统功能堆砌，AI 含量低。

## 4. 核心业务流程

### 4.1 端到端主流程

1. 用户建获客任务：填产品 / 官网 / 目标市场 / 关键词
2. 系统采集线索：搜索引擎 / 海关 / 导入 → 候选公司列表
3. AI 画像评分：LLM 抽取 → 匹配分 → 排序
4. 用户确认入池：挑高匹配公司进客户池
5. AI 生成开发信：千邮千面 + A/B 版本
6. 系统发送：带追踪像素 + 链接探针
7. 系统追踪：打开 / 点击事件回传，更新状态
8. AI Agent 跟进决策：按状态机自动走策略（循环 6→8）
9. 终止：回复 → 转人工 / 拒绝 → 停止 / 达上限 → 结束

### 4.2 客户跟进状态机

- 主链：待触达 → 已发送 → 已打开 → 已回复（成功终态）
- 回环（AI 自动决策）：未打开 → 换标题重发；未回复 → 换角度跟进
- 终态：已拒绝（明确拒绝 → 终止）、无效退信（退信 → 清洗）
- 约束：每序列设轮次上限（如 5 封），超限自动停止，避免骚扰（CAN-SPAM 合规）

## 5. 数据模型

### 5.1 核心数据表（7 张）

| 表 | 关键字段 | 说明 |
|---|---|---|
| users | id, email, password_hash | 用户账号 |
| campaigns | id, user_id, name, product_name, website, target_market, keywords, status | 获客任务 |
| companies | id, campaign_id, name, website, country, source, profile(jsonb), match_score, status | 公司线索 + LLM 画像 |
| contacts | id, company_id, name, title, email, is_decision_maker | 决策人 |
| emails | id, campaign_id, company_id, contact_id, subject, body, variant, status, model, token_usage | 开发信（A/B 变体） |
| email_events | id, email_id, event_type(open/click/reply/bounce), occurred_at | 追踪事件 |
| follow_up_steps | id, company_id, contact_id, step_no, step_type, email_id, status | 跟进序列步骤 |

### 5.2 表关系

```
users 1──N campaigns
campaigns 1──N companies
companies 1──N contacts
companies/contacts 1──N emails
emails 1──N email_events
contacts 1──N follow_up_steps
```

### 5.3 企业级设计点

1. profile 用 jsonb：LLM 画像字段灵活，不频繁改表结构。
2. email_events 事件表：打开/点击/回复/退信全部事件化，状态机靠它驱动，可审计可重放。
3. emails 记 token_usage + model：成本控制与生成质量评测的数据基础。

### 5.4 与状态机的对应

- contacts.status = 状态机节点（待触达 / 已发送 / 已打开 / 已回复 / 已拒绝 / 无效）
- email_events = 驱动状态迁移的事件
- follow_up_steps = 递进式序列的落地记录

## 6. 技术架构

### 6.1 分层架构（五层）

| 层 | 内容 | 技术 |
|---|---|---|
| 接入层 API | 对外接口 | FastAPI · REST · JWT 鉴权 |
| 业务服务层 | 业务编排 | 线索 / 画像 / 邮件生成 / 发送 / 跟进 |
| AI / Agent 层 | 智能核心 | LangGraph 状态机 · RAG · Prompt 模板 · LLM 封装 |
| 数据访问层 | 持久化 | SQLAlchemy · 仓储模式 |
| 基础设施层 | 底座 | PostgreSQL+pgvector · Redis · Celery · Qwen API |

### 6.2 技术选型

Python 3.11 / FastAPI / LangChain + LangGraph / PostgreSQL(+pgvector) / Redis + Celery / Docker / Qwen(DashScope，OpenAI 兼容)

### 6.3 企业级设计点

1. 可插拔数据源（DataSource 接口，CSV + 搜索 API，预留海关接口）
2. EmailSender 双实现（MockEmailSender + SMTPSender）
3. LangGraph 跟进状态机（LLM 条件路由）
4. LLM 统一封装（重试 / 超时 / token 统计 / 日志）
5. 配置管理（pydantic-settings）+ 结构化日志

## 7. 非功能需求

- 性能：批量生成 / 发送走 Celery 异步，单任务几千家公司可控。
- 安全：JWT 鉴权、密钥走环境变量不进代码、密码哈希存储。
- 合规：爬虫遵守目标站 robots / 限流；邮件遵守 CAN-SPAM / GDPR（退订、身份标识）；仅用公开 / 样例数据，不群发陌生人。
- 可观测：结构化日志、LLM 调用成本统计。
- 可维护：分层架构、仓储模式、配置管理、单元测试、文档。

## 8. 模块拆解与开发顺序

| 模块 | 做什么 | 验证点 |
|---|---|---|
| M0 项目脚手架 | 目录 + uv + 配置 + 日志 + Docker 骨架 | 能启动、能打日志 |
| M1 数据层 | 7 表 + SQLAlchemy + 仓储 + 迁移 | 能建表、CRUD |
| M2 线索采集 | DataSource 接口 + CSV 导入 + 样例数据 | 导入即见公司记录 |
| M3 画像匹配（AI） | LLMClient + 画像抽取 + 评分 | 公司 → 画像 + 匹配分 |
| M4 邮件生成（AI） | RAG 产品库 + few-shot + A/B | 画像 → 开发信 |
| M5 发送与追踪 | EmailSender 双实现 + 像素/探针 | 发信 → 事件 → 状态更新 |
| M6 自动跟进（AI/Agent） | LangGraph 状态机 + 跟进决策 | 事件驱动流转 + 跟进信 |
| M7 API + 前端 | FastAPI 路由 + JWT + Web 界面 | 浏览器走通全流程 |
| M8 工程化收尾 | 评测集 + 测试 + Docker 部署 + 文档 | 测试过 + 线上可访问 |

排序逻辑：依赖决定顺序（数据→采集→画像→生成→发送→跟进）；AI 主线优先（M3/M4/M6）；工程化贯穿（M0 开头、M8 收尾）。

## 9. 关键技术决策（附录）

- 不微调：用 Prompt + few-shot（in-context）+ RAG + LangGraph 工作流（显式拆思考步骤）替代。理由：场景不缺模型能力、缺业务上下文；微调要大量标注数据 + 退化风险 + 维护成本高。
- 三个落地前提：① 数据源可插拔（样例 + CSV，预留海关 / 搜索 API，不花钱）② 模型 Qwen(DashScope) ③ 邮件双实现（Mock + SMTP 自测）。
- 企业级工程标准：分层架构、LLM 统一封装、结构化日志、评测集、Docker 部署阿里云、测试、能讲架构权衡。
