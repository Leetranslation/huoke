# 项目长期记忆

## 项目定位

- 项目名：**AI 外贸获客 Agent 平台**（对外简历可叫「智能外拓获客 / AI SDR」）。
- 目标：作为应聘「智能体开发 / AI 应用开发」实习的作品集项目；对齐实习公司（外贸 AI 获客方向）真实场景。
- 对标产品：贸小七、麦穗获客（国内）；Apollo.io、Instantly、Snov.io（海外）。
- 核心流水线：线索挖掘（公开数据）→ 画像匹配（LLM 打分排序）→ 个性化触达（生成+发送+追踪）→ 自动跟进（Agent 决策）。
- AI 含量三落点：画像匹配（LLM 结构化抽取）、个性化触达（RAG+Prompt 生成开发信）、自动跟进（LangGraph 状态机+LLM 决策）。

## 技术栈（暂定，待讨论确认）

Python 3.11+ / FastAPI / LangChain + LangGraph / PostgreSQL(+pgvector) / Redis + Celery / Docker / OpenAI 兼容模型 API（Qwen 等）；爬虫 Scrapy/Playwright；邮件 smtplib 或 SES/Postmark。

## 开发规范（见 D:/YXAgent/DEVELOPING.md，最重要）

1. 讨论先行：需求没聊清楚前不写代码、不建文件、不生成文档。
2. 先讲后做：给出「做什么+为什么+预期结果」，用户明确同意才动手。
3. 收工交代：只列事实（改了什么、结果如何、什么没做成）。
4. 改道重审：中途改方向先停下重新征求同意。

## 已确定的产品结论（2026-10-11）

- 定位：AI 外贸获客 Agent 平台（B2B，仅邮件触达）。
- 完整功能清单（四段骨架，AI 三落点为核）：①线索采集（搜索引擎/海关/CSV 导入）②画像匹配🔵LLM 结构化抽取+评分+决策人识别 ③个性化触达🔵RAG+千邮千面+A/B+发送追踪 ④自动跟进🔵LangGraph 状态机+意向判断+漏斗；横向支撑=客户池/账号权限/看板。砍掉社媒/LBS/展会/建站等传统功能。
- 核心业务流程：端到端 9 步 + 跟进状态机（待触达→已发送→已打开→已回复/已拒绝/无效退信；未打开重发、未回复跟进、轮次上限）。
- 三个落地前提：①数据源可插拔（CSV+样例，预留海关/搜索 API，不花钱）②模型 Qwen(DashScope) ③邮件双实现（MockEmailSender + SMTPSender 自测）。

## 企业级工程标准（用户定调，最重要）

不做"脚本跑通"，要做企业级：分层架构 + 仓储模式、LLM 调用统一封装（成本/重试/评测）、结构化日志/错误处理/配置管理、有评测集、Docker 部署阿里云、有测试、能讲架构权衡。简历诚实定位：实习参与营销获客方向 + 独立复刻深化完整系统。

## 关键技术决策

- **不微调**：用 Prompt + few-shot（in-context）+ RAG + LangGraph 工作流（显式拆思考步骤）替代。理由：场景不缺模型能力、缺业务上下文；微调要大量标注数据 + 有退化风险 + 维护成本高。
- 架构五层：接入层 / 业务服务层 / AI Agent 层 / 数据访问层 / 基础设施层；跟进 Agent 用 LangGraph 状态机。

## 开发策略（2026-10-12 确定）

- **行走骨架（Walking Skeleton）**：先搭骨架（目录 + 接口 + 桩）→ 跑通最薄链路（导入线索→画像→生成→mock 发送→状态更新）→ 横向做厚。
- 目录结构：app/{core, models, schemas, repositories, datasources, agent, senders, services, api, tasks}；可插拔点 = datasources/ 和 senders/（base 接口 + 多实现）。
- 6 个关键接口：DataSource、EmailSender、LLMClient、Profiler、EmailWriter、FollowUpGraph。
- 协作方式：骨架/脚手架由我搭，代码实现由用户自己写（结对编程）。
