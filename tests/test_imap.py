"""测试 163 IMAP 收信。"""

import email
import imaplib
import sys

sys.stdout.reconfigure(encoding="utf-8")

HOST = "imap.163.com"
PORT = 993
USER = "ltk1475675134@163.com"
PASSWORD = "PZtsugRvSFc5r7ch"


def decode(s: str) -> str:
    if not s:
        return ""
    parts = email.header.decode_header(s)
    out = []
    for text, enc in parts:
        if isinstance(text, bytes):
            out.append(text.decode(enc or "utf-8", errors="replace"))
        else:
            out.append(text)
    return "".join(out)


def main() -> None:
    try:
        M = imaplib.IMAP4_SSL(HOST, PORT)
        M.login(USER, PASSWORD)
        # 关键：163 要求登录后发送 ID 命令标识客户端，否则 SELECT 被拒
        imaplib.Commands["ID"] = ("AUTH",)
        M._simple_command("ID", '("name" "YXAgent" "version" "1.0" "vendor" "YXAgent")')
        typ, data = M.select("INBOX")
        print(f"select 结果: typ={typ} data={data}")
        if typ != "OK":
            M.logout()
            return
        typ, data = M.search(None, "ALL")
        ids = data[0].split()
        print(f"连接成功，收件箱共 {len(ids)} 封")

        for i in ids[-6:]:
            typ, msg_data = M.fetch(i, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            print("---")
            print("From:", decode(msg["From"] or ""))
            print("Subject:", decode(msg["Subject"] or ""))
            print("Date:", msg["Date"])
        M.logout()
    except Exception as e:  # noqa: BLE001
        print(f"失败: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
