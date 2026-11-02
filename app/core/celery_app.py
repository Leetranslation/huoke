"""Celery 应用：Redis 作 broker/backend，beat 每天定时扫描跟进。"""

from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

from app.core.config import settings

celery_app = Celery(
    "yxagent",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.followup"],
)

celery_app.conf.update(
    timezone="Asia/Shanghai",
    enable_utc=False,
    task_track_started=True,
    broker_connection_retry_on_startup=True,
    beat_schedule={
        # 每天早上 9 点扫描跟进（可按需调整）
        "daily-followup-scan": {
            "task": "app.tasks.followup.daily_scan",
            "schedule": crontab(hour=9, minute=0),
        },
        # 每 3 分钟拉一次收件箱，识别客户回复
        "check-replies": {
            "task": "app.tasks.followup.check_replies",
            "schedule": timedelta(minutes=3),
        },
    },
)
