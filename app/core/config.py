"""集中配置：从 .env / 环境变量读取，全局唯一 Settings 实例。"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # 应用
    app_name: str = "yxagent"
    app_env: str = "development"

    # 数据库
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/yxagent"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # 大模型（OpenAI 兼容，默认 DeepSeek，可换 Qwen/GLM 等）
    llm_api_key: str = ""
    llm_model: str = "deepseek-chat"
    llm_base_url: str = "https://api.deepseek.com"

    # Apify（ImportYeti 海关数据爬虫）
    apify_token: str = ""

    # Tavily 搜索（找客户数据源，免费 1000 次/月）
    tavily_api_key: str = ""

    # 邮件追踪用的公网地址（本地测试填隧道地址，线上填域名）
    public_base_url: str = "http://127.0.0.1:8001"

    # 测试客户邮箱（每个获客任务自动注入，用于验证邮件追踪）
    test_contact_email: str = ""

    # 自动跟进参数
    follow_up_interval_days: int = 4  # 距上次发送超过多少天发跟进信
    follow_up_max_steps: int = 5  # 最多跟进轮次（含首封）

    # JWT
    secret_key: str = "change-me-to-a-random-secret"
    access_token_expire_minutes: int = 1440

    # 邮件
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""


settings = Settings()
