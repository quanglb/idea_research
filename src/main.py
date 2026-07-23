import os
import sys
import argparse
from src.scraper import (
    fetch_hacker_news,
    fetch_product_hunt,
    fetch_reddit,
    fetch_github_trending
)
from src.analyzer import analyze_ideas
from src.telegram_bot import send_telegram_report

def run_pipeline(debug: bool = False):
    print("Bắt đầu thu thập dữ liệu trong 12 giờ qua...")
    
    hn_ideas = fetch_hacker_news(hours=12)
    ph_ideas = fetch_product_hunt(hours=12)
    reddit_ideas = fetch_reddit(hours=12)
    github_ideas = fetch_github_trending(hours=12)
    
    all_ideas = hn_ideas + ph_ideas + reddit_ideas + github_ideas
    print(f"Tổng hợp thu thập được {len(all_ideas)} tin tức thô.")
    
    if not all_ideas:
        msg = "Không có ý tưởng mới nào được tìm thấy trong 12 giờ qua."
        print(msg)
        if not debug:
            token = os.environ.get("TELEGRAM_BOT_TOKEN")
            chat_id = os.environ.get("TELEGRAM_CHAT_ID")
            send_telegram_report(msg, token, chat_id)
        return

    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        print("Lỗi: Thiếu GEMINI_API_KEY.")
        return
        
    print("Đang gửi dữ liệu sang Gemini API để phân tích...")
    report = analyze_ideas(all_ideas, api_key=gemini_key)
    
    if debug:
        print("\n=== [DEBUG MODE] BÁO CÁO CỦA BẠN ===\n")
        print(report)
        print("\n====================================\n")
    else:
        print("Đang gửi báo cáo qua Telegram...")
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        if send_telegram_report(report, token, chat_id):
            print("Gửi báo cáo thành công!")
        else:
            print("Gửi báo cáo thất bại.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Idea Research Reporter Bot")
    parser.add_argument("--debug", action="store_true", help="Chạy chế độ debug, in ra màn hình thay vì gửi Telegram")
    args = parser.parse_args()
    
    if not args.debug:
        if not os.environ.get("TELEGRAM_BOT_TOKEN") or not os.environ.get("TELEGRAM_CHAT_ID"):
            print("Lỗi: Cần cấu hình TELEGRAM_BOT_TOKEN và TELEGRAM_CHAT_ID ở môi trường hệ thống.")
            sys.exit(1)
            
    if not os.environ.get("GEMINI_API_KEY"):
        print("Lỗi: Cần cấu hình GEMINI_API_KEY.")
        sys.exit(1)
        
    run_pipeline(debug=args.debug)
