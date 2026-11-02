"""业务状态常量（生命周期 / 邮件状态 / 事件类型分离）。"""


class ContactStatus:
    """客户生命周期：描述客户在业务中的阶段。

    注意：不包含「已打开」——打开追踪受邮件客户端隐私机制影响，不可靠，
    「打开/点击」只作为事件记录，不改变生命周期。
    """

    PENDING = "pending"              # 待分析 / 待触达
    QUALIFIED = "qualified"          # 已确认匹配
    CONTACTED = "contacted"          # 已发送，跟进中
    REPLIED = "replied"              # 已回复（转人工）
    COMPLETED = "completed"          # 已完成
    REJECTED = "rejected"            # 拒绝（终止）
    UNSUBSCRIBED = "unsubscribed"    # 退订（终止）
    INVALID = "invalid"              # 无效地址 / 硬退信（终止）
    PAUSED = "paused"                # 暂停


class EmailStatus:
    """邮件发送状态：描述单封邮件的发送过程。"""

    DRAFT = "draft"                        # 草稿
    PENDING_APPROVAL = "pending_approval"  # 待审批
    APPROVED = "approved"                  # 已批准
    SENDING = "sending"                    # 发送中
    SENT = "sent"                          # 已发送
    FAILED = "failed"                      # 发送失败


class EventType:
    """邮件事件：追加记录，不覆盖客户状态。"""

    OPEN = "open"
    CLICK = "click"
    REPLY = "reply"
    BOUNCE = "bounce"
    UNSUBSCRIBE = "unsubscribe"
    REJECTED = "rejected"
    MANUAL_NOTE = "manual_note"


class StepType:
    INITIAL = "initial"
    FOLLOW_UP = "follow_up"
    RE_ENGAGE = "re_engage"


class CampaignStatus:
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"
