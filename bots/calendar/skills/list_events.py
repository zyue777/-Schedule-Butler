from core.context import Context, ContextStatus, SkillManifest
from storage.db_manager import DBManager
from datetime import datetime
import json

MANIFEST = SkillManifest(
    name="list_events",
    description="查看今日或近期的日程",
    triggers=["今日日程", "今天日程", "本周日程", "日程", "待办"],
    version="1.0.0",
    priority=20
)

def handle(ctx: Context) -> Context:
    db = DBManager()
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    is_future = "待办" in ctx.raw_text or "未来" in ctx.raw_text or "本周" in ctx.raw_text
    
    if is_future:
        events = db.get_future_events(today_str)
        title_prefix = "📅 待办/未来日程"
    else:
        events = db.get_today_events(today_str)
        title_prefix = f"📅 今日日程 ({today_str})"
        
    if not events:
        ctx.status = ContextStatus.SUCCESS
        ctx.reply_text = f"{title_prefix} 暂无安排。"
        return ctx
        
    reply = f"{title_prefix}：\n\n"
    for ev in events:
        date_display = f"【{ev['date']}】 " if is_future else "【今日】 "
        end_display = f"-{ev['end_time']}" if ev['end_time'] else ""
        reply += f"🔹 **{date_display}{ev['start_time']}{end_display}**  {ev['title']}\n"
        
        extra = json.loads(ev['extra_json'])
        if extra.get('organizer'):
            reply += f"   🏢 机构: {extra['organizer']}\n"
        if extra.get('password'):
            reply += f"   🔑 密码: {extra['password']}\n"
        if extra.get('phone'):
            reply += f"   📞 电话: {extra['phone']}\n"
        if extra.get('links'):
            links_str = ' '.join(extra['links'])
            reply += f"   🔗 链接: {links_str}\n"
        if extra.get('notes'):
            reply += f"   📝 说明: {extra['notes']}\n"
            
        reply += f"   (ID: {ev['id']})\n\n"
        
    ctx.status = ContextStatus.SUCCESS
    ctx.reply_text = reply.strip()
    return ctx
