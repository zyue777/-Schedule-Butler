import sqlite3
import json
from pathlib import Path

class DBManager:
    def __init__(self, db_path="data/calendar.db"):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id     TEXT NOT NULL,
                    title       TEXT NOT NULL,
                    date        TEXT NOT NULL,           -- YYYY-MM-DD
                    start_time  TEXT NOT NULL,           -- HH:MM
                    end_time    TEXT DEFAULT '',         -- HH:MM
                    event_type  TEXT DEFAULT 'meeting',  -- meeting / reminder
                    repeat_rule TEXT DEFAULT 'none',     -- none / daily / weekly_1..7
                    raw_text    TEXT DEFAULT '',
                    extra_json  TEXT DEFAULT '{}',       -- 密码、电话等
                    reminded_30 INTEGER DEFAULT 0,       -- 是否已发30分钟提醒
                    reminded_5  INTEGER DEFAULT 0,       -- 是否已发5分钟提醒
                    reminded_day INTEGER DEFAULT 0,      -- 是否已发当日提醒
                    created_at  TEXT DEFAULT (datetime('now','localtime')),
                    status      TEXT DEFAULT 'active'    -- active / done / cancelled
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_events_date ON events(date, status)')

            try:
                conn.execute('ALTER TABLE events ADD COLUMN reminded_5 INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                pass


    def add_event(self, event_data: dict) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO events (
                    user_id, title, date, start_time, end_time, event_type, 
                    repeat_rule, raw_text, extra_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event_data.get('user_id'),
                event_data.get('title'),
                event_data.get('date'),
                event_data.get('start_time'),
                event_data.get('end_time', ''),
                event_data.get('event_type', 'meeting'),
                event_data.get('repeat_rule', 'none'),
                event_data.get('raw_text', ''),
                json.dumps(event_data.get('extra', {}), ensure_ascii=False)
            ))
            return cursor.lastrowid

    def get_today_events(self, date_str: str) -> list:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM events WHERE date = ? AND status = 'active' ORDER BY start_time ASC", (date_str,))
            return [dict(row) for row in cursor.fetchall()]

    def get_future_events(self, date_str: str) -> list:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM events WHERE date >= ? AND status = 'active' ORDER BY date ASC, start_time ASC", (date_str,))
            return [dict(row) for row in cursor.fetchall()]

    def mark_reminded(self, event_id: int, rem_type: str):
        if rem_type == 'day':
            col = 'reminded_day'
        elif rem_type == '30min':
            col = 'reminded_30'
        elif rem_type == '5min':
            col = 'reminded_5'
        else:
            return
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"UPDATE events SET {col} = 1 WHERE id = ?", (event_id,))

    def update_event(self, event_id: int, user_id: str, changes: dict) -> bool:
        allowed = {'title', 'date', 'start_time', 'end_time', 'repeat_rule'}
        extra_keys = {'location', 'organizer', 'password', 'phone', 'notes'}
        direct = {k: v for k, v in changes.items() if k in allowed}
        extra_changes = {k: v for k, v in changes.items() if k in extra_keys}
        try:
            with sqlite3.connect(self.db_path) as conn:
                if direct:
                    set_clause = ', '.join(f"{k} = ?" for k in direct)
                    vals = list(direct.values()) + [event_id, user_id]
                    conn.execute(
                        f"UPDATE events SET {set_clause} WHERE id = ? AND user_id = ?", vals
                    )
                if extra_changes:
                    row = conn.execute(
                        "SELECT extra_json FROM events WHERE id = ? AND user_id = ?",
                        (event_id, user_id)
                    ).fetchone()
                    existing = json.loads(row[0]) if row else {}
                    existing.update(extra_changes)
                    conn.execute(
                        "UPDATE events SET extra_json = ? WHERE id = ? AND user_id = ?",
                        (json.dumps(existing, ensure_ascii=False), event_id, user_id)
                    )
            return True
        except Exception as e:
            print(f"[DBManager] update_event 失败: {e}")
            return False

    def mark_event_done(self, event_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE events SET status = 'done' WHERE id = ?", (event_id,))

    def cleanup_expired_events(self, today_str: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("UPDATE events SET status = 'done' WHERE date < ? AND status = 'active'", (today_str,))
            return cursor.rowcount
