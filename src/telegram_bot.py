import requests

def split_message(text: str, max_chars: int = 4000) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    parts = []
    lines = text.split("\n")
    current_part = ""

    for line in lines:
        if len(current_part) + len(line) + (1 if current_part else 0) > max_chars:
            if current_part:
                parts.append(current_part)
                current_part = ""

            while len(line) > max_chars:
                parts.append(line[:max_chars])
                line = line[max_chars:]
            current_part = line
        else:
            if current_part:
                current_part += "\n" + line
            else:
                current_part = line

    if current_part:
        parts.append(current_part)

    return parts

def send_telegram_report(report_text: str, token: str, chat_id: str) -> bool:
    if not token or not chat_id:
        print("Lỗi: Thiếu TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID.")
        return False

    parts = split_message(report_text, max_chars=4000)
    success = True

    for part in parts:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": part,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        try:
            r = requests.post(url, json=payload, timeout=15)
            if r.status_code != 200:
                if "can't parse entities" in r.text or "parse" in r.text.lower():
                    print("Khôi phục: Phát hiện lỗi định dạng Markdown của Telegram, đang thử gửi lại dưới dạng văn bản thường...")
                    payload.pop("parse_mode", None)
                    r_retry = requests.post(url, json=payload, timeout=15)
                    if r_retry.status_code != 200:
                        print(f"Telegram API retry error: {r_retry.status_code} - {r_retry.text}")
                        success = False
                else:
                    print(f"Telegram API error: {r.status_code} - {r.text}")
                    success = False
        except Exception as e:
            print(f"Exception sending to Telegram: {e}")
            success = False

    return success
