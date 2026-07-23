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
Bạn là một chuyên gia phân tích xu hướng công nghệ và chiến lược kinh doanh.
Dưới đây là danh sách các ý tưởng và dự án nổi bật vừa được thu thập từ các nguồn (Hacker News, Product Hunt, Reddit, GitHub Trending,...):

```json
{ideas_summary}
```

Hãy phân tích và chọn ra:
1. **5 ideas cho Business & SaaS**: Các ý tưởng có khả năng thương mại hóa, giải quyết bài toán cụ thể của người dùng hoặc doanh nghiệp.
2. **5 ideas cho Tech & Open Source**: Các dự án công nghệ, công cụ lập trình, thư viện mã nguồn mở tiềm năng.
3. **5 ideas cho YouTube & Content**: Các chủ đề thú vị, xu hướng hot phù hợp để làm nội dung video hoặc bài viết phân tích.

**Yêu cầu định dạng:**
- Trả về kết quả bằng định dạng Vietnamese Markdown sạch đẹp, trình bày chuyên nghiệp.
- Sử dụng các tiêu đề sau:
  - `## Business & SaaS`
  - `## Tech & Open Source`
  - `## YouTube & Content`
- Với mỗi ý tưởng, trình bày rõ tên ý tưởng, nguồn/liên kết (nếu có), tóm tắt và lý do/tiềm năng đánh giá.
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

