"""Channel 抽象基类。"""
from abc import ABC, abstractmethod
from core.context import Context


class ChannelBase(ABC):
    @abstractmethod
    def start(self, runtime):
        """启动监听（可阻塞）。"""
        pass

    @abstractmethod
    def send_reply(self, ctx: Context):
        """将结果发回用户。"""
        pass

    def build_context(self, runtime, **kwargs) -> Context:
        # 解析 channel 名称：优先类属性 → 模块级 MANIFEST → 兜底 unknown
        manifest = getattr(self.__class__, 'MANIFEST', None)
        if manifest is None:
            import sys
            mod = sys.modules.get(self.__class__.__module__)
            manifest = getattr(mod, 'MANIFEST', None)
        channel_name = manifest.name if manifest else 'unknown'
        return Context(
            bot_name=runtime.config.name,
            channel=channel_name,
            workspace=runtime.config.workspace,
            **kwargs,
        )
