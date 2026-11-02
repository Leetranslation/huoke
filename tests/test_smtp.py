"""测试 SMTP 真实发信。"""

import sys

from app.senders.smtp_sender import SMTPSender

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    sender = SMTPSender()
    result = sender.send(
        to="3793458109@qq.com",
        subject="YXAgent 测试邮件",
        body="这是一封来自 YXAgent 的测试邮件，用于验证 SMTP 发信。",
        html=(
            "<p>这是一封来自 <b>YXAgent</b> 的测试邮件。</p>"
            "<p>如果你看到这封邮件，说明 SMTP 发信已打通。</p>"
        ),
    )
    print("ok:", result.ok)
    print("message:", result.message)


if __name__ == "__main__":
    main()
