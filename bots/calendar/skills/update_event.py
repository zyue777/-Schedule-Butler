import re
import json
import sqlite3
from core.context import Context, ContextStatus, SkillManifest
from core.i18n import detect_lang, t
from storage.db_manager import DBManager

MANIFEST = SkillManifest(
    name="update_event",
    description="修改已有日程",
    triggers=["修改", "change", "update", "edit"],
    version="1.0.0",
    priority=25
)

UPDATE_PROMPT = """You are a schedule modification assistant. The user gives a change instruction — output ONLY the changed fields as JSON (omit unchanged fields).
你是日程修改助手。用户给出修改指令，只输出需要变更的字段 JSON。

Editable fields: title, date (YYYY-MM-DD), start_time (HH:MM), end_time (HH:MM), location, notes, password

Output pure JSON only, no code blocks, no explanation. Examples:
{"start_time": "08:00"}
{"date": "2026-05-01", "start_time": "14:00"}
{"title": "Team dinner"}"""

def handle(ctx: Context) -> Context:
    raw = ctx.raw_text.strip()
    lang = detect_lang(raw)

    # 提取第一个数字作为 event_id
    m = re.search(r'\d+', raw)
    if not m:
        ctx.status = ContextStatus.SUCCESS
        ctx.reply_text = t('update_no_id', lang)
        return ctx

    event_id = int(m.group())
    # 修改意图 = 去掉触发词和ID后的剩余文字
    intent = raw[m.end():].strip()
    if not intent:
        ctx.status = ContextStatus.SUCCESS
        ctx.reply_text = t('update_no_intent', lang, id=event_id)
        return ctx

    db = DBManager()

    # 验证权限
    with sqlite3.connect(db.db_path) as conn:
        row = conn.execute(
            "SELECT id, title FROM events WHERE id = ? AND user_id = ? AND status = 'active'",
            (event_id, ctx.user_id)
        ).fetchone()
    if not row:
        ctx.status = ContextStatus.SUCCESS
        ctx.reply_text = t('update_not_found', lang, id=event_id)
        return ctx

    # 用统一 LLMClient 解析修改意图
    try:
        from tools.llm_client import LLMClient
        llm = LLMClient()
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d %A')

        system_content = UPDATE_PROMPT + f"\n\n【今天日期】{today}"
        headers = {
            "Authorization": f"Bearer {llm.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": llm.model,
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": intent}
            ],
            "temperature": 0.1
        }
        import requests as _req
        resp = _req.post(
            llm.api_url,
            headers=headers,
            json=payload, timeout=30
        )
        changes_str = resp.json()['choices'][0]['message']['content'].strip()
        changes_str = changes_str.strip('`').strip()
        if changes_str.startswith('json'):
            changes_str = changes_str[4:]
        changes = json.loads(changes_str)
    except Exception as e:
        ctx.status = ContextStatus.SUCCESS
        ctx.reply_text = t('update_parse_fail', lang, id=event_id)
        return ctx

    if not changes:
        ctx.status = ContextStatus.SUCCESS
        ctx.reply_text = t('update_empty', lang, id=event_id)
        return ctx

    ok = db.update_event(event_id, ctx.user_id, changes)
    if ok:
        changed_desc = ", ".join(
            f"{k}→{v}" for k, v in changes.items()
            if k in ('title', 'date', 'start_time', 'end_time', 'location', 'notes', 'password')
        )
        ctx.status = ContextStatus.SUCCESS
        ctx.reply_text = t('update_ok', lang, id=event_id, title=row[1], desc=changed_desc)
    else:
        ctx.status = ContextStatus.SUCCESS
        ctx.reply_text = t('update_fail', lang)

    return ctx
