import json
from dataclasses import dataclass
from typing import Optional

@dataclass
class ParsedEvent:
    title: str           # 事项标题
    date: str            # YYYY-MM-DD
    start_time: str      # HH:MM
    end_time: str        # HH:MM (可空)
    event_type: str      # meeting / reminder / habit
    repeat: str          # none / daily / weekly_X
    raw_text: str        # 原始文本
    extra: dict          # 地点、密码、电话等附加信息

class EventParser:
    def parse_llm_json(self, json_str: str, raw_text: str = "") -> Optional[ParsedEvent]:
        if not json_str:
            return None
            
        try:
            data = json.loads(json_str)
            
            # 如果大模型认为没有会议内容，可能会返回空的或者不包含核心时间
            if not data.get('date') or not data.get('start_time'):
                return None
                
            extra = {}
            if data.get('location'): extra['location'] = data['location']
            if data.get('organizer'): extra['organizer'] = data['organizer']
            if data.get('password'): extra['password'] = data['password']
            if data.get('phone'): extra['phone'] = data['phone']
            if data.get('links'): extra['links'] = data['links']
            if data.get('notes'): extra['notes'] = data['notes']

            event_type = data.get('event_type', 'meeting')
            if event_type not in ('meeting', 'reminder', 'habit'):
                event_type = 'meeting'

            repeat = data.get('repeat_rule', 'none') or 'none'

            return ParsedEvent(
                title=data.get('title', '未命名日程'),
                date=data.get('date', ''),
                start_time=data.get('start_time', ''),
                end_time=data.get('end_time', ''),
                event_type=event_type,
                repeat=repeat,
                raw_text=raw_text,
                extra=extra
            )
        except json.JSONDecodeError:
            print(f"[EventParser] 解析 LLM 返回的 JSON 失败: {json_str}")
            return None
