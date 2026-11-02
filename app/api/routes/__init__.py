"""路由汇总。"""

from app.api.routes import campaigns, companies, emails, followup, tracking

routers = [
    campaigns.router,
    companies.router,
    emails.router,
    followup.router,
    tracking.router,
]
