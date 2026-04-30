"""统一时区工具：所有业务逻辑通过 now() 获取当前时间，确保与 .env TIMEZONE 一致。"""
import os
from datetime import datetime, timezone, timedelta

_tz = None

def _get_tz():
    global _tz
    if _tz is None:
        tz_str = os.environ.get("TIMEZONE", "Asia/Shanghai")
        try:
            import zoneinfo
            _tz = zoneinfo.ZoneInfo(tz_str)
        except Exception:
            # Python < 3.9 fallback or missing tzdata
            try:
                from dateutil import tz as dtz
                _tz = dtz.gettz(tz_str)
            except Exception:
                # Last resort: parse common offset formats
                _tz = None
    return _tz

def now() -> datetime:
    """返回带时区的当前时间，使用 .env 中的 TIMEZONE 配置。"""
    tz = _get_tz()
    if tz:
        return datetime.now(tz)
    return datetime.now()

def today_str() -> str:
    """返回今天日期字符串 YYYY-MM-DD"""
    return now().strftime('%Y-%m-%d')

def now_hm() -> str:
    """返回当前时间 HH:MM"""
    return now().strftime('%H:%M')

def today_weekday() -> str:
    """返回今天日期 + 星期，如 2026-04-30 Wednesday"""
    return now().strftime('%Y-%m-%d %A')
