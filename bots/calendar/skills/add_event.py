import os
from datetime import datetime, timedelta
from core.context import Context, ContextStatus, SkillManifest
from tools.event_parser import EventParser
from storage.db_manager import DBManager

MANIFEST = SkillManifest(
    name="add_event",
    description="自动解析会议通知并入库",
    triggers=["添加", "新增"],
    version="1.0.0",
    priority=10
)

def handle(ctx: Context) -> Context:
    text = ctx.raw_text
    
    from tools.kimi_client import KimiClient
    kimi = KimiClient()
    llm_json_str = ""
    
    # 1. OCR + LLM 解析 (图片路线)
    if not text and ctx.metadata.get('has_image'):
        runtime = ctx.metadata.get('_runtime')
        if runtime:
            from tools.feishu_token import FeishuTokenManager
            import urllib.request
            
            app_id = ctx.metadata.get('app_id')
            app_secret = ctx.metadata.get('app_secret')
            message_id = ctx.metadata.get('message_id')
            image_key = ctx.metadata.get('image_key')
            
            token_mgr = FeishuTokenManager(app_id, app_secret)
            token = token_mgr.get_tenant_access_token()
            
            try:
                # download image
                url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/resources/{image_key}?type=image"
                req = urllib.request.Request(url, headers={
                    "Authorization": f"Bearer {token}",
                    "User-Agent": "Mozilla/5.0",
                })
                with urllib.request.urlopen(req, timeout=60) as resp:
                    img_bytes = resp.read()
                
                print("[add_event] 开始调用 Kimi 视觉 API 进行多模态解析...")
                llm_json_str = kimi.extract_event_from_bytes(img_bytes)
                text = "图片日程记录" # Fallback raw text placeholder
            except Exception as e:
                ctx.status = ContextStatus.ERROR
                ctx.error_message = f"图片处理/解析失败: {e}"
                return ctx
    
    # 2. 纯文本 LLM 解析 (文本路线)
    elif text:
        try:
            print("[add_event] 开始调用 Kimi API 进行纯文本结构化解析...")
            llm_json_str = kimi.extract_event_from_text(text)
        except Exception as e:
            ctx.status = ContextStatus.ERROR
            ctx.error_message = f"文本智能解析失败: {e}"
            return ctx

    # 3. 将 JSON 转换为 Event
    parser = EventParser()
    event = parser.parse_llm_json(llm_json_str, raw_text=text)
    
    if not event:
        ctx.status = ContextStatus.SUCCESS
        ctx.reply_text = "❓ 未识别到日程，如需记录请发含时间的事项\n例：明天下午3点开会 / 今晚7点去伊利汇 / 每天早8点吃药"
        return ctx
        
    db = DBManager()
    event_dict = {
        'user_id': ctx.user_id,
        'title': event.title,
        'date': event.date,
        'start_time': event.start_time,
        'end_time': event.end_time,
        'event_type': event.event_type,
        'repeat_rule': event.repeat,
        'raw_text': event.raw_text,
        'extra': event.extra
    }
    
    event_id = db.add_event(event_dict)
    
    # 计算提醒时间（开始前30分钟）
    try:
        start_dt = datetime.strptime(f"{event.date} {event.start_time}", "%Y-%m-%d %H:%M")
        remind_dt = start_dt - timedelta(minutes=30)
        remind_str = remind_dt.strftime("%H:%M")
    except Exception:
        remind_str = ""

    lines = [f"✅ 已记录 #{event_id}"]
    lines.append(f"📌 {event.title}")
    time_line = f"📅 {event.date}  {event.start_time}"
    if event.end_time:
        time_line += f" - {event.end_time}"
    lines.append(time_line)
    if event.extra.get('location'):
        lines.append(f"📍 {event.extra['location']}")
    if event.extra.get('organizer'):
        lines.append(f"🏢 {event.extra['organizer']}")
    if event.extra.get('password'):
        lines.append(f"🔑 密码: {event.extra['password']}")
    if event.extra.get('phone'):
        lines.append(f"📞 {event.extra['phone']}")
    if event.extra.get('links'):
        lines.append(f"🔗 {' '.join(event.extra['links'])}")
    if event.extra.get('notes'):
        lines.append(f"📝 {event.extra['notes']}")
    if remind_str:
        lines.append(f"⏰ {remind_str} 会提醒你")
    lines.append(f"─────\n有误？发「修改 {event_id} 时间为8点」或「删除 {event_id}」")

    ctx.status = ContextStatus.SUCCESS
    ctx.reply_text = "\n".join(lines)
    return ctx
