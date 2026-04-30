import json
from datetime import datetime

class TelegramCardBuilder:
    @staticmethod
    def build_daily_briefing(date_str: str, events: list) -> str:
        content = f"📅 **明日日程 · {date_str}**\n\n"
        if not events:
            return content + "明日暂无日程安排"
            
        for ev in events:
            extra = json.loads(ev['extra_json'])
            time_str = ev['start_time']
            if ev.get('end_time'):
                time_str += f"-{ev['end_time']}"
            content += f"⏰ {time_str}  {ev['title']}\n"
            if extra.get('location'):
                content += f"📍 {extra['location']}\n"
            if extra.get('organizer'):
                content += f"🏢 {extra['organizer']}\n"
            if extra.get('password'):
                content += f"🔑 密码: {extra['password']}\n"
            if extra.get('phone'):
                content += f"📞 {extra['phone']}\n"
            if extra.get('links'):
                links_str = ' '.join(extra['links'])
                content += f"🔗 {links_str}\n"
            if extra.get('notes'):
                content += f"📝 {extra['notes']}\n"
            content += "\n"

        content += f"⏱️ 20:00 · 日程管家自动推送"
        return content

    @staticmethod
    def build_30min_reminder(event: dict) -> str:
        extra = json.loads(event['extra_json'])
        time_str = event['start_time']
        if event.get('end_time'):
            time_str += f"-{event['end_time']}"
            
        content = f"⚠️ **日程即将开始 · 30分钟后**\n\n"
        content += f"**事项:** {event['title']}\n**时间:** {time_str}\n"
        if extra.get('location'):
            content += f"**地点:** {extra['location']}\n"
        if extra.get('organizer'):
            content += f"**机构:** {extra['organizer']}\n"
        if extra.get('password'):
            content += f"**密码:** {extra['password']}\n"
        if extra.get('phone'):
            content += f"**电话:** {extra['phone']}\n"
        if extra.get('links'):
            links_str = ' '.join(extra['links'])
            content += f"**链接:** {links_str}\n"
        if extra.get('notes'):
            content += f"**说明:** {extra['notes']}\n"
            
        content += f"\n⏱️ {datetime.now().strftime('%H:%M')} · 日程管家自动推送"
        return content

    @staticmethod
    def build_5min_reminder(event: dict) -> str:
        extra = json.loads(event['extra_json'])
        time_str = event['start_time']
        if event.get('end_time'):
            time_str += f"-{event['end_time']}"
            
        content = f"🚨 **日程马上开始 · 5分钟后**\n\n"
        content += f"**事项:** {event['title']}\n**时间:** {time_str}\n"
        if extra.get('location'):
            content += f"**地点:** {extra['location']}\n"
        if extra.get('organizer'):
            content += f"**机构:** {extra['organizer']}\n"
        if extra.get('password'):
            content += f"**密码:** {extra['password']}\n"
        if extra.get('phone'):
            content += f"**电话:** {extra['phone']}\n"
        if extra.get('links'):
            links_str = ' '.join(extra['links'])
            content += f"**链接:** {links_str}\n"
        if extra.get('notes'):
            content += f"**说明:** {extra['notes']}\n"
            
        content += f"\n⏱️ {datetime.now().strftime('%H:%M')} · 日程管家自动推送"
        return content
