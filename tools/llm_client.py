import os
import json
import base64
import requests
from datetime import datetime

PROMPT = """You are a schedule assistant. Extract event info from the user's message into structured JSON.
你是日程助手，从用户消息中提取日程信息并输出 JSON。

[Rules]
- Message has BOTH a time word AND an action → extract as event
- No time info or not an event → output: {}
- Multiple agenda items → extract only the main meeting/event
- Use the reference date from system message for relative dates (today/tomorrow/next week)

[Output] Pure JSON only, no markdown, no explanation. Fixed field order:
{
  "title": "Event name (≤ 20 chars, e.g.: Team standup / Take vitamins / Product launch)",
  "event_type": "meeting | reminder | habit",
  "organizer": "Organizer name (empty string if none)",
  "date": "YYYY-MM-DD",
  "start_time": "HH:MM",
  "end_time": "HH:MM (empty string if none)",
  "location": "Place or URL (empty string if none)",
  "repeat_rule": "none | daily | weekly_N (N=1 Mon..7 Sun)",
  "password": "Meeting password (empty string if none)",
  "phone": "Phone number (empty string if none)",
  "links": ["url1"],
  "notes": "Extra notes (empty string if none)"
}"""

class LLMClient:
    def __init__(self):
        self.api_key = os.environ.get('LLM_API_KEY')
        self.api_url = os.environ.get('LLM_API_URL', 'https://api.moonshot.cn/v1/chat/completions')
        self.model = os.environ.get('LLM_MODEL', 'moonshot-v1-8k')
        
    def _call_api(self, content_messages) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        today = datetime.now().strftime('%Y-%m-%d %A')
        system_content = PROMPT + f"\n\n【今天日期】{today}"

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_content
                },
                {
                    "role": "user",
                    "content": content_messages
                }
            ],
            "temperature": 0.1
        }
        
        try:
            resp = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                content = data['choices'][0]['message']['content']
                # 简单过滤可能存在的 markdown 代码块
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                elif content.startswith('```'):
                    content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                return content.strip()
            else:
                error_msg = f"HTTP错误: {resp.status_code} - {resp.text}"
                print(f"[LLMClient] {error_msg}")
                raise Exception(f"大模型解析失败: {error_msg}")
        except Exception as e:
            print(f"[LLMClient] 异常: {e}")
            raise e

    def extract_event_from_bytes(self, image_bytes: bytes) -> str:
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        content = [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            }
        ]
        return self._call_api(content)
        
    def extract_event_from_text(self, text: str) -> str:
        content = [
            {
                "type": "text",
                "text": text
            }
        ]
        return self._call_api(content)
