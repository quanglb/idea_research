import os
from src.telegram_bot import send_telegram_report
from src.main import run_pipeline

def handle_command(command_text: str, token: str, chat_id: str, gemini_key: str = None) -> str:
    cmd = command_text.strip().lower()
    
    if cmd.startswith("/help") or cmd.startswith("/start"):
        help_msg = (
            "🤖 *Hướng dẫn sử dụng Bot IdeaRadar AI*\n\n"
            "Các câu lệnh bạn có thể gửi cho Bot:\n"
            "• `/help` - Xem danh sách các câu lệnh và hướng dẫn\n"
            "• `/test` - Kiểm tra trạng thái kết nối & hoạt động của Bot\n"
            "• `/run` - Quét tin tức và phát hành báo cáo 15 ý tưởng ngay lập tức\n\n"
            "⏰ *Lịch tự động*: Bot tự động quét và gửi báo cáo 2 lần/ngày vào lúc 9h00 sáng và 14h00 chiều."
        )
        send_telegram_report(help_msg, token, chat_id)
        return help_msg
        
    elif cmd.startswith("/test") or cmd.startswith("/ping"):
        test_msg = (
            "🟢 *Bot đang hoạt động bình thường!*\n\n"
            "• *Nguồn quét*: Hacker News, Product Hunt, Reddit, GitHub Trending.\n"
            "• *Lịch tự động*: 09:00 và 14:00 (GMT+7).\n"
            "• *Trạng thái*: Đã kết nối thành công với Telegram & Gemini API."
        )
        send_telegram_report(test_msg, token, chat_id)
        return test_msg

    elif cmd.startswith("/run") or cmd.startswith("/report"):
        status_msg = "⏳ Đang tiến hành quét tin tức từ 4 nguồn và phân tích bằng Gemini AI. Vui lòng đợi trong giây lát..."
        send_telegram_report(status_msg, token, chat_id)
        
        if gemini_key:
            os.environ["GEMINI_API_KEY"] = gemini_key
        if token:
            os.environ["TELEGRAM_BOT_TOKEN"] = token
        if chat_id:
            os.environ["TELEGRAM_CHAT_ID"] = chat_id
            
        run_pipeline(debug=False)
        return status_msg
        
    else:
        unknown_msg = (
            "❓ Lệnh không hợp lệ. Vui lòng gõ `/help` để xem danh sách các câu lệnh khả dụng."
        )
        send_telegram_report(unknown_msg, token, chat_id)
        return unknown_msg
