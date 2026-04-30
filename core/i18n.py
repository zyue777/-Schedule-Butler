"""轻量级双语支持：根据用户输入自动判断语言，返回对应文案。"""
import re

# 检测是否为中文输入（含至少一个中文字符）
_CN_PATTERN = re.compile(r'[\u4e00-\u9fff]')

def detect_lang(text: str) -> str:
    """返回 'zh' 或 'en'"""
    return 'zh' if _CN_PATTERN.search(text) else 'en'

# ─── 文案字典 ───
_STRINGS = {
    # guide_skill
    'guide': {
        'zh': """🤖 日程管家使用指南
━━━━━━━━━━━━━━━━━
直接发任何事项即可录入，例如：
• 今晚7点吃火锅
• 明天下午3点开会，密码1234
• 每天早8点吃维生素
• 发送会议邀请截图 → 自动识别

📋 常用指令：
• 日程 / 待办 → 查看日程列表
• 修改 [ID] [改什么] → 修改日程
  例：修改 3 时间为8点
• 删除 [ID] → 取消日程
• 指南 → 重新显示本帮助

⏰ 提醒规则：
• 每晚20:00 推送明日日程汇总
• 每个事项前30分钟自动提醒
• 事项结束后自动标记完成""",
        'en': """🤖 Schedule Butler User Guide
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Just send any event and it will be recorded, e.g.:
• Dinner at 7pm tonight
• Meeting tomorrow 3pm, password 1234
• Take vitamins daily at 8am
• Send a meeting invite screenshot → auto-parsed

📋 Commands:
• schedule / todo → View your events
• change [ID] [what] → Modify an event
  e.g.: change 3 time to 8am
• delete [ID] → Cancel an event
• help → Show this guide again

⏰ Reminder Rules:
• 8:00 PM daily → Tomorrow's schedule briefing
• 30 minutes before → Upcoming event alert
• After event ends → Auto-marked as done""",
    },

    # add_event
    'add_no_event': {
        'zh': "❓ 未识别到日程，如需记录请发含时间的事项\n例：明天下午3点开会 / 今晚7点吃火锅 / 每天早8点吃药",
        'en': "❓ No event detected. Please include a time in your message.\ne.g.: Meeting tomorrow at 3pm / Dinner tonight at 7 / Take meds daily at 8am",
    },
    'add_confirm': {
        'zh': "⏰ {remind} 会提醒你\n─────\n有误？发「修改 {id} 时间为8点」或「删除 {id}」",
        'en': "⏰ Reminder at {remind}\n─────\nWrong? Send \"change {id} time to 8am\" or \"delete {id}\"",
    },
    'add_confirm_no_remind': {
        'zh': "─────\n有误？发「修改 {id} 时间为8点」或「删除 {id}」",
        'en': "─────\nWrong? Send \"change {id} time to 8am\" or \"delete {id}\"",
    },

    # list_events
    'list_todo_title': {
        'zh': "📋 待办清单（{start} ~ {end}）",
        'en': "📋 To-Do List ({start} ~ {end})",
    },
    'list_week_title': {
        'zh': "📅 本周日程（{start} ~ {end}）",
        'en': "📅 This Week ({start} ~ {end})",
    },
    'list_today_title': {
        'zh': "📅 今日日程（{date}）",
        'en': "📅 Today's Schedule ({date})",
    },
    'list_empty': {
        'zh': "暂无安排 ✨",
        'en': "No events scheduled ✨",
    },

    # delete_event
    'delete_no_id': {
        'zh': "请提供要删除的日程ID，例如：删除 1",
        'en': "Please provide an event ID, e.g.: delete 1",
    },
    'delete_bad_id': {
        'zh': "日程ID必须是数字，例如：删除 1",
        'en': "Event ID must be a number, e.g.: delete 1",
    },
    'delete_not_found': {
        'zh': "❌ 未找到 ID 为 {id} 的日程，或者您无权删除。",
        'en': "❌ Event #{id} not found, or you don't have permission.",
    },
    'delete_ok': {
        'zh': "✅ 已成功取消日程: {title} (ID: {id})",
        'en': "✅ Event cancelled: {title} (ID: {id})",
    },
    'delete_fail': {
        'zh': "❌ 删除失败: {err}",
        'en': "❌ Delete failed: {err}",
    },

    # update_event
    'update_no_id': {
        'zh': "请指定要修改的日程 ID，例如：修改 3 时间为8点",
        'en': "Please specify an event ID, e.g.: change 3 time to 8am",
    },
    'update_no_intent': {
        'zh': "请说明要改什么，例如：修改 {id} 时间为8点",
        'en': "Please specify what to change, e.g.: change {id} time to 8am",
    },
    'update_not_found': {
        'zh': "❌ 未找到 ID 为 {id} 的日程，或已取消。",
        'en': "❌ Event #{id} not found or already cancelled.",
    },
    'update_parse_fail': {
        'zh': "❌ 解析修改内容失败，请换种说法，例如：修改 {id} 时间为8点",
        'en': "❌ Could not parse your change. Try: change {id} time to 8am",
    },
    'update_empty': {
        'zh': "❓ 未识别到要修改的内容，请说明，例如：修改 {id} 时间为8点",
        'en': "❓ No changes detected. Try: change {id} time to 8am",
    },
    'update_ok': {
        'zh': "✅ 已修改 #{id}（{title}）\n{desc}",
        'en': "✅ Updated #{id} ({title})\n{desc}",
    },
    'update_fail': {
        'zh': "❌ 修改失败，请稍后再试。",
        'en': "❌ Update failed. Please try again later.",
    },
}


def t(key: str, lang: str, **kwargs) -> str:
    """获取文案，支持 format 占位符。"""
    entry = _STRINGS.get(key, {})
    text = entry.get(lang, entry.get('en', f'[{key}]'))
    if kwargs:
        text = text.format(**kwargs)
    return text
