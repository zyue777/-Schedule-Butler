"""Bot 发现、加载、启动。"""
import os
import re
import yaml
import threading
import subprocess
import sys
from pathlib import Path
from core.registry import Registry
from core.bot_runtime import BotRuntime, BotConfig

class BotLoader:
    def __init__(self, project_root: Path):
        self.root = project_root
        self.global_tools = Registry("global/tools")
        self.global_hooks = Registry("global/hooks")
        self.global_providers = Registry("global/providers")

        self.global_tools.discover(str(project_root / 'tools'), 'tools')
        
        hooks_dir = project_root / 'hooks'
        if hooks_dir.exists():
            self.global_hooks.discover(str(hooks_dir), 'hooks')
            
        providers_dir = project_root / 'providers'
        if providers_dir.exists():
            self.global_providers.discover(str(providers_dir), 'providers')

    def discover_and_load(self) -> list[BotRuntime]:
        runtimes = []
        bots_dir = self.root / 'bots'
        for bot_dir in sorted(bots_dir.iterdir()):
            if not bot_dir.is_dir() or bot_dir.name.startswith('_'):
                continue
            cfg_file = bot_dir / 'bot.yaml'
            if not cfg_file.exists():
                continue
            try:
                raw = cfg_file.read_text(encoding='utf-8')
                
                # Fetch envs manually if not present
                for key in ['FEISHU_APP_ID', 'FEISHU_APP_SECRET']:
                    if key in os.environ:
                        raw = raw.replace(f"${{{key}}}", os.environ[key])
                        
                data = yaml.safe_load(raw) or {}
                
                # Ensure correct nested parsing before constructing dataclass
                config_kwargs = {}
                for k in BotConfig.__dataclass_fields__:
                    if k in data:
                        config_kwargs[k] = data[k]
                
                config = BotConfig(**config_kwargs)
                
                rt = BotRuntime(config, bot_dir, self.global_tools, self.global_hooks, self.global_providers)
                runtimes.append(rt)
                print(f"[loader] 成功加载 Bot: {bot_dir.name}")
                
            except Exception as e:
                print(f"[loader] 加载 {bot_dir.name} 失败: {e}")
                
        return runtimes
