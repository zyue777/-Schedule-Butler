from core.context import Context, ContextStatus, SkillManifest

MANIFEST = SkillManifest(
    name="guide_skill",
    description="显示使用指南",
    triggers=["指南", "帮助", "help"],
    version="1.0.0",
    priority=50
)

GUIDE_TEXT = """🤖 日程管家使用指南
━━━━━━━━━━━━━━━━━
直接发任何事项即可录入，例如：
• 今晚7点去伊利汇
• 明天下午3点开会，密码1234
• 每天早8点吃二甲双胍2片
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
• 事项结束后自动标记完成"""


def handle(ctx: Context) -> Context:
    ctx.status = ContextStatus.SUCCESS
    ctx.reply_text = GUIDE_TEXT
    return ctx
