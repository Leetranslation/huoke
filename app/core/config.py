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

    # 大模型
    dashscope_api_key: str = ""
    llm_model: str = "qwen-plus"
    llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # JWT
    secret_key: str = "change-me-to-a-random-secret"
    access_token_expire_minutes: int = 1440

    # 邮件
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""


settings = Settings()
