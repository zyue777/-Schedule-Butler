# 📅 日程管家 (Calendar Butler) — 飞书 Bot 实现方案

## 目标

构建一个**零 LLM 依赖**的飞书机器人，用户通过飞书私聊推送文字/图片形式的会议安排或生活提醒，Bot 自动解析并录入日历，在**当天早晨 8:00** 和**会议前 30 分钟**通过飞书卡片主动提醒。

---

## User Review Required

> [!IMPORTANT]
> **飞书应用需要新建**：日程管家需要一个独立的飞书应用（独立的 APP_ID / APP_SECRET），不能复用健康管家的，否则 WebSocket 连接会冲突。你需要去 [飞书开放平台](https://open.feishu.cn) 创建一个新应用，开启「机器人」能力和 `im:message:receive_v1` 事件。

> [!IMPORTANT]
> **图片识别策略选择**：图片会议通知的 OCR 有两个方案：
> - **方案 A（推荐）**：调用飞书自带的 [OCR 识别 API](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/ai/optical_char_recognition-v1/image/basic_recognize)（免费，无需额外 Key，但需要在飞书后台开通 AI 能力）
> - **方案 B**：复用你现有的 Kimi/DeepSeek 视觉 API（需消耗 Token，但识别更智能）
> 
> 目前计划采用 **方案 A** — 飞书原生 OCR + 正则解析。如果你更倾向用 AI 识别，请告知。

> [!WARNING]  
> **GitHub 仓库**：需要在 GitHub 创建新仓库 `zyue777/calendar-butler`（或你偏好的名字），并配置 `SERVER_SSH_KEY`、`SERVER_HOST`、`SERVER_USER`、`ENV_FILE` 四个 Secrets。

---

## Open Questions

1. **你的飞书 open_id**：当前健康管家硬编码了你的 `ou_cceaf266a7a2d44ff99d4c74aa7973aa`。日程管家的提醒也发给这个用户吗？还是有其他人也需要收到？
2. **会议年份推断**：你的会议格式只写「4月27日」不写年份。系统默认推断为当前年份（如已过去则推断为明年），这个逻辑可以接受吗？
3. **提醒频率**：目前计划是「当天 08:00 晨报卡片 + 会议前 30 分钟单独卡片」，是否还需要「前一天晚上预告」？
4. **OCR 降级**：如果飞书 OCR API 开通不了，是否接受降级到 Kimi 视觉 API？

---

## 核心设计：零 LLM 的纯规则引擎

### 为什么不需要大模型？

你的会议通知有**高度结构化的格式**（标题 + `时间：` + `参会密码：` 等固定字段）。对于这类模式，正则表达式的准确率远超 LLM（100% 确定性 vs. LLM 的概率性），且零成本、零延迟。

对于非结构化的提醒（如「提醒我吃药」「每天下午3点吃保健品」），也只需一套关键词 + 时间模式匹配，完全不需要 AI。

```
用户输入 → 正则/规则引擎解析 → SQLite 落盘 → APScheduler 定时扫描 → 飞书卡片推送
```

---

## 架构设计

### 复用健康管家的 5 层框架

日程管家的代码结构 **100% 克隆** 自健康管家（`core/`、`channels/`、`tools/` 完全复用），只更换业务层：

```
日程管家/
├── .env                          # 飞书应用配置（新应用）
├── .env.example
├── .github/workflows/deploy.yml  # CI/CD（克隆自健康管家）
├── .gitignore
├── CLAUDE.md                     # Agent 入口文档
├── ecosystem.config.cjs          # PM2 配置
├── main.py                       # 统一入口
├── requirements.txt
├── start.sh                      # 本地调试启动
│
├── core/                         # 🔴 100% 复用健康管家核心
│   ├── __init__.py
│   ├── bot_loader.py
│   ├── bot_runtime.py
│   ├── context.py                # 精简版（去掉 mood/memory_ctx 等健康专属字段）
│   ├── executor.py               # 精简版（去掉周期注入）
│   ├── middleware.py
│   ├── pending_store.py
│   ├── registry.py
│   └── router.py                 # 重写：日程管家专用路由
│
├── channels/
│   ├── __init__.py
│   ├── base.py                   # 复用
│   └── feishu_ws.py              # 复用（图片+文字合并机制完美适配）
│
├── bots/
│   └── calendar/
│       ├── bot.yaml              # 日程管家 Bot 配置
│       └── skills/
│           ├── add_event.py      # 核心：解析 + 入库
│           ├── list_events.py    # 查看今日/本周日程
│           ├── delete_event.py   # 删除日程
│           └── simple_remind.py  # 简单提醒（吃药等）
│
├── tools/
│   ├── __init__.py
│   ├── feishu_token.py           # 复用
│   ├── feishu_message.py         # 复用
│   ├── feishu_card.py            # [NEW] 卡片消息发送（从 db_receipt.py 提炼）
│   ├── feishu_ocr.py             # [NEW] 飞书 OCR API 封装
│   ├── image_download.py         # 复用
│   ├── event_parser.py           # [NEW] 核心正则解析引擎
│   └── reminder_engine.py        # [NEW] APScheduler 提醒引擎
│
├── storage/
│   └── db_manager.py             # [NEW] SQLite 日程数据库
│
├── data/                         # 运行时数据（git ignore）
│   └── calendar.db
└── logs/
```

---

## Proposed Changes

### 1. 核心解析引擎 `tools/event_parser.py`

这是整个系统的大脑 — 纯 Python 正则引擎，零 LLM 依赖。

**解析策略**：

```python
# 模式 1：结构化会议通知
# 匹配 "时间：4月27日（周一）16:00-17:00"
TIME_PATTERN = r'时间[：:]\s*(\d{1,2})月(\d{1,2})日.*?(\d{1,2}:\d{2})\s*[-–~]\s*(\d{1,2}:\d{2})?'

# 匹配 "4月30日（周四）08:30" (无结束时间)
TIME_PATTERN_2 = r'(\d{1,2})月(\d{1,2})日\s*[（(].*?[）)]\s*(\d{1,2}:\d{2})'

# 匹配标题：《xxx》格式
TITLE_PATTERN = r'《(.+?)》'

# 匹配参会密码
PASSWORD_PATTERN = r'(?:参会密码|会议密码|密码)[：:]\s*(\S+)'

# 匹配接入号码
PHONE_PATTERN = r'(?:接入号码|拨入号码)[：:](.+?)(?=\n\n|⚠|$)'

# 模式 2：简单提醒
# "提醒我下午3点吃药" → 解析为 daily/one-shot reminder
REMIND_PATTERN = r'提醒我(.+?)(?:(\d{1,2})[点:：](\d{0,2}))?(.+)'

# 模式 3: 每天/每周重复
REPEAT_DAILY = r'每天\s*(\d{1,2})[点:：](\d{0,2})'
REPEAT_WEEKLY = r'每(?:周|个星期)([一二三四五六日天])\s*(\d{1,2})[点:：](\d{0,2})'
```

**输出结构**：
```python
@dataclass
class ParsedEvent:
    title: str           # 会议标题 / 提醒内容
    date: str            # YYYY-MM-DD
    start_time: str      # HH:MM
    end_time: str        # HH:MM (可空)
    event_type: str      # meeting / reminder
    repeat: str          # none / daily / weekly_X
    raw_text: str        # 原始文本（存档）
    extra: dict          # 密码、电话等附加信息
```

---

### 2. SQLite 数据库 `storage/db_manager.py`

```sql
CREATE TABLE events (
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
    reminded_30 INTEGER DEFAULT 0,      -- 是否已发30分钟提醒
    reminded_day INTEGER DEFAULT 0,     -- 是否已发当日提醒
    created_at  TEXT DEFAULT (datetime('now','localtime')),
    status      TEXT DEFAULT 'active'   -- active / done / cancelled
);
CREATE INDEX idx_events_date ON events(date, status);
```

---

### 3. 提醒引擎 `tools/reminder_engine.py`

使用 `APScheduler` 每分钟扫描一次数据库，检查是否有需要提醒的事件。

```python
# 两个提醒触发点：
# 1. 当天 08:00 — 晨报卡片（汇总今日所有日程）
# 2. 会议前 30 分钟 — 单独卡片（含密码、电话等详细信息）

scheduler = BackgroundScheduler(timezone='Asia/Shanghai')

# 每天 08:00 发送晨报
scheduler.add_job(send_daily_briefing, 'cron', hour=8, minute=0)

# 每分钟扫描 30 分钟提醒
scheduler.add_job(check_30min_reminders, 'interval', minutes=1)
```

---

### 4. 飞书卡片模板 `tools/feishu_card.py`

#### 晨报卡片（当天 08:00）
```
┌─────────────────────────────────┐
│  📅 今日日程 · 2026年4月27日     │  (蓝色头)
├─────────────────────────────────┤
│  🔵 16:00-17:00                 │
│  棉花专家交流                    │
│  密码: 116375                   │
│                                 │
│  🟢 19:00-20:00                 │
│  东鹏饮料业绩交流会              │
│                                 │
│  💊 15:00  吃保健品              │
├─────────────────────────────────┤
│  ⏱️ 08:00 · 日程管家自动推送     │
└─────────────────────────────────┘
```

#### 30 分钟预告卡片
```
┌─────────────────────────────────┐
│  ⏰ 会议即将开始 · 30分钟后      │  (橙色头)
├─────────────────────────────────┤
│  **会议:** 棉花专家交流          │
│  **时间:** 16:00-17:00          │
│  **密码:** 116375               │
│  **电话:** 4009698928           │
├─────────────────────────────────┤
│  ⏱️ 15:30 · 日程管家自动推送     │
└─────────────────────────────────┘
```

---

### 5. 图片 OCR `tools/feishu_ocr.py`

利用飞书开放平台的 OCR API（`/open-apis/optical_char_recognition/v1/image/basic_recognize`），将图片转为文字后，走同一套正则解析流水线。

流程：
```
图片消息 → feishu_ws.py 下载图片 → feishu_ocr.py OCR → event_parser.py 解析 → 入库
```

---

### 6. 路由器 `core/router.py`

日程管家的路由极其简单，不需要 AI 兜底：

| 优先级 | 匹配条件 | 路由到 |
|--------|---------|--------|
| 1 | 有图片 | `add_event`（先 OCR 再解析） |
| 2 | 含「时间：」或「提醒我」或日期格式 | `add_event` |
| 3 | 「今日」「今天」「本周」「日程」 | `list_events` |
| 4 | 「删除」「取消」+ 序号 | `delete_event` |
| 5 | 其他 | 简单回复使用帮助 |

---

### 7. Bot 配置 `bots/calendar/bot.yaml`

```yaml
name: calendar
label: "📅 日程管家"
enabled: true
channel: feishu_ws
ai_provider: ""           # 不需要 AI！
channels: [feishu]
hooks: [dedup, timer, audit]
allowed_users: []
```

---

### 8. PM2 & 部署

#### [NEW] `ecosystem.config.cjs`
```javascript
module.exports = {
  apps: [{
    name: "calendar-bot",
    script: "venv/bin/python",
    args: "-u main.py",
    interpreter: "none",
    autorestart: true,
    watch: false,
    log_date_format: "YYYY-MM-DD HH:mm Z",
    env: {
      PYTHONUNBUFFERED: "1",
      http_proxy: "http://127.0.0.1:10809",
      https_proxy: "http://127.0.0.1:10809",
      all_proxy: "socks5://127.0.0.1:10808"
    }
  }]
};
```

#### [NEW] `.github/workflows/deploy.yml`
克隆自健康管家，修改 `target: "/opt/apps/calendar_butler"`。

---

## 文件清单（按创建顺序）

| # | 文件 | 类型 | 说明 |
|---|------|------|------|
| 1 | `storage/db_manager.py` | NEW | SQLite 日程数据库 |
| 2 | `tools/event_parser.py` | NEW | 正则解析引擎 |
| 3 | `tools/feishu_card.py` | NEW | 飞书卡片构建 + 发送 |
| 4 | `tools/feishu_ocr.py` | NEW | 飞书 OCR 封装 |
| 5 | `tools/reminder_engine.py` | NEW | APScheduler 提醒引擎 |
| 6 | `tools/feishu_token.py` | COPY | 从健康管家复制 |
| 7 | `tools/feishu_message.py` | COPY | 从健康管家复制 |
| 8 | `tools/image_download.py` | COPY | 从健康管家复制 |
| 9 | `core/*.py` | COPY+MODIFY | 复制核心框架，精简适配 |
| 10 | `channels/base.py` | COPY | 复用 |
| 11 | `channels/feishu_ws.py` | COPY+MODIFY | 精简（去掉健康管家专属逻辑） |
| 12 | `bots/calendar/bot.yaml` | NEW | Bot 配置 |
| 13 | `bots/calendar/skills/add_event.py` | NEW | 添加日程 |
| 14 | `bots/calendar/skills/list_events.py` | NEW | 查看日程 |
| 15 | `bots/calendar/skills/delete_event.py` | NEW | 删除日程 |
| 16 | `bots/calendar/skills/simple_remind.py` | NEW | 简单提醒 |
| 17 | `main.py` | NEW | 入口 |
| 18 | `ecosystem.config.cjs` | NEW | PM2 |
| 19 | `.github/workflows/deploy.yml` | NEW | CI/CD |
| 20 | `.env.example` | NEW | 环境变量模板 |
| 21 | `.gitignore` | NEW | |
| 22 | `requirements.txt` | NEW | 依赖 |
| 23 | `CLAUDE.md` | NEW | Agent 入口文档 |

---

## Verification Plan

### Automated Tests

1. **解析引擎单元测试**：用你给的会议通知样本 + 东鹏饮料图片 OCR 结果作为测试用例
   ```bash
   cd /home/zy/桌面/日程管家
   python -m pytest tests/test_parser.py -v
   ```

2. **数据库读写测试**：
   ```bash
   python -c "from storage.db_manager import CalendarDB; db = CalendarDB(); print(db.get_today_events('test'))"
   ```

3. **本地端到端启动测试**：
   ```bash
   python main.py
   # 在飞书发送会议通知文字 → 确认卡片回执
   ```

### Manual Verification

1. 在飞书向新 Bot 发送你给出的棉花专家会议文本 → 确认解析正确并返回确认卡片
2. 发送东鹏饮料会议图片 → 确认 OCR + 解析成功
3. 发送「提醒我下午3点吃保健品」→ 确认识别并入库
4. 等待提醒时间到来 → 确认卡片推送
5. `git push` → 确认 GitHub Actions 部署到云端正常
