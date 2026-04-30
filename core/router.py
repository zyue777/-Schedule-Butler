"""
日程管家专用路由器：纯规则，无 AI 依赖。
所有未匹配触发词的消息，默认进入 add_event 进行正则解析。
"""
from core.context import Context, ContextStatus

class Router:
    def __init__(self, skill_registry, phase_configs=None, pending_store=None):
        self._skill_reg = skill_registry
        self._pending_store = pending_store

    def route(self, ctx: Context) -> Context:
        text = ctx.raw_text.strip()

        # 第1层：精确指令匹配（如"删除 123", "今天", "本周"）
        matches = self._skill_reg.match_by_trigger(text)
        if matches:
            best = matches[0]
            ctx.matched_skill = best['name']
            ctx.match_confidence = 1.0
            remainder = text[len(best['trigger']):].strip()
            ctx.parsed_args = {'content': remainder} if remainder else {}
            ctx.status = ContextStatus.ROUTED
            return ctx

        # 第2层：默认全量路由给 add_event (由正则引擎接管)
        # 包含图片和普通的日程文本
        if text or ctx.metadata.get('image_keys'):
            ctx.matched_skill = 'add_event'
            ctx.match_confidence = 0.8
            ctx.status = ContextStatus.ROUTED
            return ctx

        ctx.status = ContextStatus.ERROR
        ctx.error_message = "不支持的消息类型或空消息"
        return ctx
