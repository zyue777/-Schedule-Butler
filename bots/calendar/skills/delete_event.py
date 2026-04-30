from core.context import Context, ContextStatus, SkillManifest
from core.i18n import detect_lang, t
from storage.db_manager import DBManager

MANIFEST = SkillManifest(
    name="delete_event",
    description="删除日程记录",
    triggers=["删除日程", "删除", "取消日程", "delete", "cancel"],
    version="1.0.0",
    priority=30
)

def handle(ctx: Context) -> Context:
    lang = detect_lang(ctx.raw_text)
    args = ctx.parsed_args.get('content', '').strip()
    if not args:
        ctx.status = ContextStatus.ERROR
        ctx.reply_text = t('delete_no_id', lang)
        return ctx
        
    try:
        event_id = int(args)
    except ValueError:
        ctx.status = ContextStatus.ERROR
        ctx.reply_text = t('delete_bad_id', lang)
        return ctx
        
    db = DBManager()
    import sqlite3
    try:
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.execute("SELECT id, title FROM events WHERE id = ? AND user_id = ?", (event_id, ctx.user_id))
            event = cursor.fetchone()
            
            if not event:
                ctx.status = ContextStatus.ERROR
                ctx.reply_text = t('delete_not_found', lang, id=event_id)
                return ctx
                
            conn.execute("UPDATE events SET status = 'cancelled' WHERE id = ?", (event_id,))
            
        ctx.status = ContextStatus.SUCCESS
        ctx.reply_text = t('delete_ok', lang, title=event[1], id=event_id)
    except Exception as e:
        ctx.status = ContextStatus.ERROR
        ctx.reply_text = t('delete_fail', lang, err=str(e))
        
    return ctx
