import os
from pathlib import Path
import signal
import sys
from dotenv import load_dotenv
from core.bot_loader import BotLoader
from tools.reminder_engine import ReminderEngine
from storage.db_manager import DBManager
from core.registry import Registry

def main():
    # 1. 加载环境变量
    load_dotenv()
    
    # 2. 从 .env 加载核心配置 (Channel 在各自的 runtime 校验)
    active_bot = os.environ.get("ACTIVE_BOT", "calendar")

    # 3. 初始化数据库和定时任务
    print("初始化数据库和定时任务...")
    db_manager = DBManager()
    engine = ReminderEngine(db_manager)
    engine.start()

    # 4. 加载并运行 Bot
    bot_name = "calendar"
    project_root = Path(__file__).parent
    
    print(f"[{bot_name}] 正在启动服务...")
    
    loader = BotLoader(project_root)
    runtimes = loader.discover_and_load()
    if not runtimes:
        print("错误: 没有找到有效的机器人配置。")
        sys.exit(1)
        
    runtime = runtimes[0]

    # 直接使用 Registry 实例化 channel
    ch_registry = Registry("channels")
    ch_registry.discover(str(project_root / 'channels'), 'channels')
    channel = ch_registry.get_instance(runtime.config.channel)
    
    if not channel:
        print(f"[{bot_name}] 错误: 找不到 channel: {runtime.config.channel}。")
        sys.exit(1)
        
    # 优雅退出
    def graceful_exit(signum, frame):
        print("\n正在停止服务...")
        engine.scheduler.shutdown()
        try:
            channel.stop()
        except AttributeError:
            pass
        sys.exit(0)
        
    signal.signal(signal.SIGINT, graceful_exit)
    signal.signal(signal.SIGTERM, graceful_exit)
    
    # 开始接收消息
    channel.start(runtime)

if __name__ == "__main__":
    main()
