from core.context import Context, ContextStatus, SkillManifest
from storage.db_manager import DBManager

MANIFEST = SkillManifest(
    name="delete_event",
    description="删除日程记录",
    triggers=["删除日程", "删除", "取消日程"],
    version="1.0.0",
    priority=30
)

def handle(ctx: Context) -> Context:
    args = ctx.parsed_args.get('content', '').strip()
    if not args:
        ctx.status = ContextStatus.ERROR
        ctx.reply_text = "请提供要删除的日程ID，例如：删除 1"
        return ctx
        
    try:
        event_id = int(args)
    except ValueError:
        ctx.status = ContextStatus.ERROR
        ctx.reply_text = "日程ID必须是数字，例如：删除 1"
        return ctx
        
    db = DBManager()
    import sqlite3
    try:
        with sqlite3.connect(db.db_path) as conn:
            # 检查事件是否存在并属于当前用户
            cursor = conn.execute("SELECT id, title FROM events WHERE id = ? AND user_id = ?", (event_id, ctx.user_id))
            event = cursor.fetchone()
            
            if not event:
                ctx.status = ContextStatus.ERROR
                ctx.reply_text = f"❌ 未找到 ID 为 {event_id} 的日程，或者您无权删除。"
                return ctx
                
            conn.execute("UPDATE events SET status = 'cancelled' WHERE id = ?", (event_id,))
            
        ctx.status = ContextStatus.SUCCESS
        ctx.reply_text = f"✅ 已成功取消日程: {event[1]} (ID: {event_id})"
    except Exception as e:
        ctx.status = ContextStatus.ERROR
        ctx.reply_text = f"❌ 删除失败: {str(e)}"
        
    return ctx
