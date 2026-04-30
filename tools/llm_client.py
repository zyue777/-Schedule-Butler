import os
import json
import base64
import requests
from datetime import datetime

PROMPT = """你是一个全能日程管家助手，从用户消息中识别日程、提醒、计划。

【识别范围】
- 会议、电话会、路演、发布会、业绩说明会等正式会议
- 餐厅预约、聚餐、约会等社交事项
- 吃药、打针、体检等医疗提醒
- 断食、运动、健身等健康计划
- 临时备忘（去某地、取件、约人等）
- 其他任何含时间的待办事项

【识别标准】
同时满足：① 含时间词（几点/今天/明天/下周/每天/X月X日等）② 含要做的事 → 识别为日程。
完全无时间信息且不像日程 → 输出：{}

【特殊规则】
- 行程单含多个环节（签到/吃饭/乘车/核心会议）：只提取核心交流/会议时段
- phone 只保留中国大陆境内/400电话，海外号码不录入
- 图片或文字中没有任何日程信息 → 输出：{}

【日期处理】
参考 system 消息中的今日日期做相对日期推算：
今天/今晚 = 今日，明天/明日 = 明日，后天 = 后日，具体日期直接转换

【输出规范】纯 JSON 无代码块，字段固定顺序：
{
  "title": "事项名称（简洁≤20字，如：去伊利汇 / 吃二甲双胍 / 巨星农牧业绩交流会）",
  "event_type": "meeting 或 reminder 或 habit（三选一）",
  "organizer": "主办方/机构名称（无则空字符串）",
  "date": "YYYY-MM-DD",
  "start_time": "HH:MM",
  "end_time": "HH:MM（无则空字符串）",
  "location": "地点/会议室/网址（无则空字符串）",
  "repeat_rule": "none 或 daily 或 weekly_N（N=1周一..7周日）",
  "password": "会议密码（无则空字符串）",
  "phone": "国内电话，多号码用/分隔（无则空字符串）",
  "links": ["网址1"],
  "notes": "补充说明（如：吃2片随餐/断食16小时/无则空字符串）"
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
