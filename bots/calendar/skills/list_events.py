from core.context import Context, ContextStatus, SkillManifest
from core.i18n import detect_lang, t
from storage.db_manager import DBManager
from datetime import datetime, timedelta
import json

MANIFEST = SkillManifest(
    name="list_events",
    description="查看今日或近期的日程",
    triggers=["今日日程", "今天日程", "本周日程", "日程", "待办", "todo", "schedule", "this week"],
    version="1.0.0",
    priority=20
)

def handle(ctx: Context) -> Context:
    lang = detect_lang(ctx.raw_text)
    db = DBManager()
    today_str = datetime.now().strftime('%Y-%m-%d')

    raw_lower = ctx.raw_text.lower()
    is_todo = "待办" in ctx.raw_text or "todo" in raw_lower
    is_week = "本周" in ctx.raw_text or "未来" in ctx.raw_text or "this week" in raw_lower

    if is_todo:
        end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        events = db.get_week_events(today_str, end_date, ctx.user_id)
        title_prefix = t('list_todo_title', lang, start=today_str, end=end_date)
    elif is_week:
        end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        events = db.get_week_events(today_str, end_date, ctx.user_id)
        title_prefix = t('list_week_title', lang, start=today_str, end=end_date)
    else:
        events = db.get_today_events(today_str, ctx.user_id)
        title_prefix = t('list_today_title', lang, date=today_str)

    if not events:
        ctx.status = ContextStatus.SUCCESS
        ctx.reply_text = f"{title_prefix}\n{t('list_empty', lang)}"
        return ctx

    reply = f"{title_prefix}：\n\n"
    for ev in events:
        if is_todo or is_week:
            date_display = f"【{ev['date']}】 "
        else:
            date_display = ""
        end_display = f"-{ev['end_time']}" if ev['end_time'] else ""
        reply += f"🔹 {date_display}{ev['start_time']}{end_display}  {ev['title']}\n"

        extra = json.loads(ev['extra_json'])
        if extra.get('organizer'):
            reply += f"   🏢 {extra['organizer']}\n"
        if extra.get('password'):
            reply += f"   🔑 {extra['password']}\n"
        if extra.get('phone'):
            reply += f"   📞 {extra['phone']}\n"
        if extra.get('links'):
            reply += f"   🔗 {' '.join(extra['links'])}\n"
        if extra.get('notes'):
            reply += f"   📝 {extra['notes']}\n"

        reply += f"   (ID: {ev['id']})\n\n"

    ctx.status = ContextStatus.SUCCESS
    ctx.reply_text = reply.strip()
    return ctx
