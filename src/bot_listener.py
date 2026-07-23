import os
import sys
import time
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.telegram_commands import handle_command

def start_bot_listener():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    if not token or not chat_id:
        print("Lỗi: Cần cấu hình TELEGRAM_BOT_TOKEN và TELEGRAM_CHAT_ID.")
        return

    print("🤖 Bot listener đang chạy... Đang lắng nghe các lệnh từ Telegram (/help, /test, /run)...")
    offset = 0
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates?offset={offset}&timeout=20"
            r = requests.get(url, timeout=25)
            if r.status_code == 200:
                data = r.json()
                for result in data.get("result", []):
                    offset = result["update_id"] + 1
                    message = result.get("message", {})
                    text = message.get("text", "")
                    sender_id = str(message.get("chat", {}).get("id", ""))
                    
                    if text.startswith("/") and sender_id == chat_id:
                        print(f"Nhận lệnh từ Telegram: {text}")
                        handle_command(text, token=token, chat_id=chat_id, gemini_key=gemini_key)
        except Exception as e:
            print(f"Lỗi listener: {e}")
            time.sleep(5)

if __name__ == "__main__":
    start_bot_listener()
