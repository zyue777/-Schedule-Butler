import os
import json
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from storage.db_manager import DBManager
from tools.feishu_message import FeishuMessageSender
from tools.feishu_token import FeishuTokenManager
from tools.feishu_card import FeishuCardBuilder

class ReminderEngine:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager
        timezone_str = os.environ.get("TIMEZONE", "Asia/Shanghai")
        self.scheduler = BackgroundScheduler(timezone=timezone_str)
        
        active_bot = os.environ.get("ACTIVE_BOT", "feishu")
        if active_bot == "telegram":
            from channels.telegram.sender import TelegramSender
            from channels.telegram.card import TelegramCardBuilder
            self.msg_sender = TelegramSender()
            self.card_builder = TelegramCardBuilder
        else:
            app_id = os.environ.get("FEISHU_APP_ID", "")
            app_secret = os.environ.get("FEISHU_APP_SECRET", "")
            from tools.feishu_token import FeishuTokenManager
            from tools.feishu_message import FeishuMessageSender
            self.token_manager = FeishuTokenManager(app_id, app_secret)
            self.msg_sender = FeishuMessageSender(self.token_manager)
            from tools.feishu_card import FeishuCardBuilder
            self.card_builder = FeishuCardBuilder
        
        # Schedule jobs
        self.scheduler.add_job(self.send_daily_briefing, 'cron', hour=20, minute=0)
        self.scheduler.add_job(self.check_30min_reminders, 'interval', minutes=1)
        self.scheduler.add_job(self.check_5min_reminders, 'interval', minutes=1)
        self.scheduler.add_job(self.check_event_completion, 'interval', minutes=1)
        self.scheduler.add_job(self.clean_expired_events, 'cron', hour=0, minute=5)
        
    def start(self):
        self.scheduler.start()
        print("[ReminderEngine] 提醒引擎已启动")
        
    def send_daily_briefing(self):
        print("[ReminderEngine] 执行晚报推送（次日日程）")
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_str = tomorrow.strftime('%Y-%m-%d')

        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM events WHERE date = ? AND status = 'active' ORDER BY start_time ASC",
                (tomorrow_str,)
            )
            all_events = [dict(row) for row in cursor.fetchall()]

        users_events = {}
        for ev in all_events:
            users_events.setdefault(ev['user_id'], []).append(ev)

        for user_id, events in users_events.items():
            card_data = self.card_builder.build_daily_briefing(tomorrow_str, events)
            self.msg_sender.send_card(user_id, card_data)
                
    def check_30min_reminders(self):
        now = datetime.now()
        target_time = now + timedelta(minutes=30)
        today_str = now.strftime('%Y-%m-%d')
        target_hm = target_time.strftime('%H:%M')
        
        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            # 找到今天、未发送30分钟提醒、且时间在 30 分钟内 (或者刚刚过)的事件
            cursor = conn.execute("""
                SELECT * FROM events 
                WHERE date = ? AND status = 'active' AND reminded_30 = 0 
                AND start_time <= ? AND start_time > ?
            """, (today_str, target_hm, now.strftime('%H:%M')))
            events = [dict(row) for row in cursor.fetchall()]
            
        for ev in events:
            card_data = self.card_builder.build_30min_reminder(ev)
            self.msg_sender.send_card(ev['user_id'], card_data)
            self.db.mark_reminded(ev['id'], '30min')
            print(f"[ReminderEngine] 触发30分钟提醒: {ev['title']}")

    def check_5min_reminders(self):
        now = datetime.now()
        target_time = now + timedelta(minutes=5)
        today_str = now.strftime('%Y-%m-%d')
        target_hm = target_time.strftime('%H:%M')
        
        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM events 
                WHERE date = ? AND status = 'active' AND reminded_5 = 0 
                AND start_time <= ? AND start_time > ?
            """, (today_str, target_hm, now.strftime('%H:%M')))
            events = [dict(row) for row in cursor.fetchall()]
            
        for ev in events:
            card_data = self.card_builder.build_5min_reminder(ev)
            self.msg_sender.send_card(ev['user_id'], card_data)
            self.db.mark_reminded(ev['id'], '5min')
            print(f"[ReminderEngine] 触发5分钟提醒: {ev['title']}")

    def check_event_completion(self):
        now = datetime.now()
        today_str = now.strftime('%Y-%m-%d')
        current_hm = now.strftime('%H:%M')

        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT id, title, end_time FROM events
                WHERE date = ? AND status = 'active' AND end_time != '' AND end_time <= ?
            """, (today_str, current_hm))
            expired = [dict(row) for row in cursor.fetchall()]

        for ev in expired:
            self.db.mark_event_done(ev['id'])
            print(f"[ReminderEngine] 自动标记完成: {ev['title']} (end_time={ev['end_time']})")

    def clean_expired_events(self):
        today_str = datetime.now().strftime('%Y-%m-%d')
        count = self.db.cleanup_expired_events(today_str)
        if count > 0:
            print(f"[ReminderEngine] 夜间自动清理：将 {count} 个历史日程标记为 done")
