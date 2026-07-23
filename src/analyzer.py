import json
import logging
from google import genai

logger = logging.getLogger(__name__)

def analyze_ideas(raw_ideas: list[dict], api_key: str) -> str:
    """
    Analyzes raw ideas using Gemini API (gemini-2.5-flash model) and produces a 
    curated summary in Vietnamese Markdown across three categories:
    - 5 ideas for Business & SaaS
    - 5 ideas for Tech & Open Source
    - 5 ideas for YouTube & Content
    """
    if not raw_ideas:
        return "Không có ý tưởng nào để phân tích."

    try:
        client = genai.Client(api_key=api_key)
        
        ideas_summary = json.dumps(raw_ideas, ensure_ascii=False, indent=2)

        prompt = f"""
Bạn là một chuyên gia phân tích xu hướng công nghệ, chiến lược kinh doanh và sáng tạo nội dung.
Dưới đây là danh sách các bài đăng thô được thu thập từ 4 nguồn nghiên cứu: Hacker News, Product Hunt, Reddit (r/sideproject, r/saas) và GitHub Trending:

```json
{ideas_summary}
```

Hãy lọc bỏ các bài rác và chọn ra chính xác:
- 5 ý tưởng tiềm năng nhất cho **Kinh doanh & SaaS**
- 5 ý tưởng tiềm năng nhất cho **Công nghệ & Open-Source**
- 5 ý tưởng làm nội dung **YouTube & Content**

⚠️ **YÊU CẦU TRÌNH BÀY ĐẶC BIỆT DÀNH CHO TELEGRAM MOBILE:**
1. Trình bày thoáng, dễ đọc trên di động, sử dụng emoji làm đầu dòng.
2. KHÔNG dùng thẻ code block (```) cho phần văn bản. Chỉ dùng chữ in đậm `*...*` cho tiêu đề và các nhãn.
3. BẮT BUỘC mỗi ý tưởng phải kèm theo đường link nguồn gốc rõ ràng dạng: `🌐 Nguồn nghiên cứu: [Tên nguồn & bài gốc](link)`.

Tuân thủ nghiêm ngặt cấu trúc dưới đây:

📅 BÁO CÁO Ý TƯỞNG AI NGHIÊN CỨU MỚI NHẤT
🔍 Nguồn nghiên cứu: Hacker News, Product Hunt, Reddit, GitHub Trending

💡 I. KINH DOANH & SAAS (5 ý tưởng)
─────────────────────────────
1. 🚀 *[Tên ý tưởng]*
📌 *Tóm tắt*: [Tóm tắt 1-2 câu súc tích]
🌐 *Nguồn nghiên cứu*: [Tên nguồn](Link bài gốc)
⭐ *Tiềm năng kinh doanh*: [Điểm/10] - [Lý do ngắn]
🤖 *Khả năng code bằng AI*: [Điểm/10] - [Gợi ý công cụ như Cursor/Lovable/Bolt.new]

2. ... (lần lượt đến 5)

🛠 II. CÔNG NGHỆ & OPEN-SOURCE (5 ý tưởng)
─────────────────────────────
1. ⚙️ *[Tên công cụ / Dự án]*
📌 *Tóm tắt tính năng*: [Tóm tắt 1-2 câu]
🌐 *Nguồn nghiên cứu*: [Tên nguồn](Link bài gốc)
🎯 *Ứng dụng thực tế*: [Gợi ý áp dụng vào công việc]
💻 *Techstack gợi ý*: [Gợi ý công nghệ]

2. ... (lần lượt đến 5)

📹 III. Ý TƯỞNG YOUTUBE & CONTENT (5 ý tưởng)
─────────────────────────────
1. 🎬 *[Tiêu đề video gợi ý]*
📌 *Chủ đề cốt lõi*: [Chủ đề công nghệ/kinh doanh làm gốc]
🌐 *Nguồn nghiên cứu*: [Tên nguồn](Link bài gốc)
💡 *Góc kịch bản*: [Gợi ý góc tiếp cận thu hút]
🖼 *Thumbnail*: [Gợi ý ý tưởng ảnh thu nhỏ]

2. ... (lần lượt đến 5)
"""
        
        models_to_try = ["gemini-flash-latest", "gemini-2.0-flash-001", "gemini-3.5-flash", "gemini-flash-lite-latest"]
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                logger.warning(f"Thử model {model_name} thất bại: {e}, thử model tiếp theo...")
                continue
                
        return "Lỗi: Tất cả các mô hình Gemini thử nghiệm đều không khả dụng."
    except Exception as e:
        logger.error(f"Lỗi khi gọi Gemini API trong analyze_ideas: {e}")
        return f"Lỗi khi phân tích ý tưởng: {str(e)}"

