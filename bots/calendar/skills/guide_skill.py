from core.context import Context, ContextStatus, SkillManifest
from core.i18n import detect_lang, t

MANIFEST = SkillManifest(
    name="guide_skill",
    description="显示使用指南",
    triggers=["指南", "帮助", "help", "guide"],
    version="1.0.0",
    priority=50
)


def handle(ctx: Context) -> Context:
    lang = detect_lang(ctx.raw_text)
    ctx.status = ContextStatus.SUCCESS
    ctx.reply_text = t('guide', lang)
    return ctx
