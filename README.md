# 📅 Schedule Butler (日程管家)

An **all-in-one cross-platform life and memory assistant**. Whether it's a business meeting, student classes, outdoor activities, or daily medication reminders, just send a simple message. The Schedule Butler will alert you at the critical moments so you never miss an important event again!

*[For the Chinese version, please scroll down. / 中文说明请见下方]*

## 🌟 Key Features
- **All-Scenario Coverage**: Supports work meetings, assignment deadlines, doctor appointments, medication routines, and more.
- **Natural Language Parsing**: Just tell the bot "Take blood pressure medicine tomorrow at 3 PM" or "Raid night on Friday at 8 PM". It automatically extracts the time and event and saves it.
- **Tiered Reminder System**:
  - **20:00 the day before**: A daily briefing of tomorrow's schedule.
  - **30 minutes before**: An upcoming event warning.
  - **5 minutes before**: An urgent "starting now" red alert.
- **Cross-Platform Multi-Channel Support**:
  - **Telegram (Recommended for Overseas)**: Seamless integration, lightweight, and stable.
  - **Feishu / Lark (Recommended for China)**: Supports OCR for images and rich-text card notifications.

---

## 🚀 Easy One-Click Deployment (For Beginners)

Whether you are on Windows, Mac, or Linux, there is no complex setup required:

1. **Prerequisites**: Make sure you have `Python 3.10+` installed on your computer.
2. **Copy Config**: Copy the `.env.example` file in the directory and rename it to `.env`.
3. **Fill in Tokens**: Open `.env` with a text editor. Fill in your bot channel configuration (e.g., Telegram Bot Token) and your LLM settings. It is compatible with any OpenAI-format API. Example configurations:
   - **Kimi (Moonshot)**:
     ```env
     LLM_API_KEY="sk-..."
     LLM_API_URL="https://api.moonshot.cn/v1/chat/completions"
     LLM_MODEL="moonshot-v1-8k"
     ```
   - **DeepSeek**:
     ```env
     LLM_API_KEY="sk-..."
     LLM_API_URL="https://api.deepseek.com/chat/completions"
     LLM_MODEL="deepseek-chat"
     ```
   - **OpenAI (ChatGPT)**:
     ```env
     LLM_API_KEY="sk-..."
     LLM_API_URL="https://api.openai.com/v1/chat/completions"
     LLM_MODEL="gpt-4o-mini"
     ```
4. **One-Click Start**:
   - **Windows**: Double-click `start.bat`.
   - **Mac**: Double-click `start_mac.command` in Finder. *(First time: right-click → Open → Open)*
   - **Linux**: Run `bash start.sh` in your terminal.

The script will automatically create a virtual environment, install necessary dependencies, and start the bot!

---

## 📱 Mobile Deployment

### Android (via Termux) ✅
Your Android phone can run Schedule Butler 24/7 as a personal server:

```bash
# 1. Install Termux from F-Droid (not Play Store)
#    https://f-droid.org/packages/com.termux/

# 2. Set up Python environment
pkg update && pkg upgrade
pkg install python git

# 3. Clone and configure
git clone https://github.com/YOUR_USER/schedule-butler.git
cd schedule-butler
cp .env.example .env
nano .env   # Fill in your tokens

# 4. Launch
bash start.sh

# 5. (Optional) Keep running after closing Termux
pkg install termux-services
# Then use: nohup bash start.sh &
```

> 💡 **Tip**: To prevent Android from killing Termux in the background, go to **Settings → Battery → Termux → Unrestricted**.

### iPhone / iPad ❌
iOS does not allow background Python processes. Recommended alternatives:
- Deploy on a cloud server (e.g., a $5/mo VPS) and access via Telegram on your phone.
- Run on a home PC/Mac and use Telegram on your phone.

---

## 🛠️ Docker Deployment (For Geeks)
If you prefer using Docker to keep your environment clean:
```bash
docker-compose up -d
```

---

## 📝 Supported Commands
| Command | Function | Uses Token? |
|---------|----------|:-----------:|
| *(any text with a time)* | Add a new event via natural language | ✅ Yes |
| `todo` / `待办` | List all events within the next 7 days | ❌ No |
| `today's schedule` | View today's arrangements | ❌ No |
| `this week` | View this week's schedule | ❌ No |
| `delete 1` | Cancel the event with ID 1 | ❌ No |
| `change 1 time to 8 AM` | Modify an existing event | ✅ Yes |
| `help` / `guide` | Show the user guide | ❌ No |

## 💡 Token-Saving Architecture

Schedule Butler is designed to be **extremely token-efficient**. Out of all operations, **only 2 consume LLM tokens**:

1. **Adding an event** — The LLM extracts structured data (time, title, location, etc.) from your natural language message. *One call per event.*
2. **Modifying an event** — The LLM interprets your change intent (e.g., "change time to 8 AM"). *One call per modification.*

Everything else — listing, deleting, reminders, daily briefings — runs on **pure rule-based logic and local database queries** with zero API calls. This means you can query your schedule hundreds of times a day without spending a single token.

---

## 🤖 Open-Source / Local Model Support

Schedule Butler is fully compatible with locally hosted open-source models via [Ollama](https://ollama.com), [LM Studio](https://lmstudio.ai), or any OpenAI-compatible API server.

### Recommended Models
| Model | Size | Quality | Notes |
|-------|------|:-------:|-------|
| **Gemma 3 27B** | 27B | ⭐⭐⭐ | Best quality, needs 16GB+ VRAM |
| **Gemma 3 14B** | 14B | ⭐⭐⭐ | Excellent, runs on 8GB+ VRAM |
| **Qwen 2.5 14B** | 14B | ⭐⭐⭐ | Strong Chinese + English |
| **Gemma 3 7B** | 7B | ⭐⭐ | Good for most tasks, occasional field omission |
| **Qwen 2.5 7B** | 7B | ⭐⭐ | Solid bilingual performance |
| **Gemma 3 4B** | 4B | ⭐ | Runs on phones (Android/Termux), English-only recommended |
| **Gemma 3 1B** | 1B | ❌ | Too small for reliable structured JSON output |

### Ollama Setup Example
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull gemma3:7b

# It auto-starts an OpenAI-compatible server at localhost:11434
```

Then configure `.env`:
```env
LLM_API_KEY="ollama"
LLM_API_URL="http://localhost:11434/v1/chat/completions"
LLM_MODEL="gemma3:7b"
```

---
---

# 📅 日程管家 (Schedule Butler)

一个**全能型的跨平台生活记忆助手**。无论是工作开会、学生上课、户外活动，还是日常的吃药提醒，只需发一条消息，日程管家就会在关键时刻准时提醒你，不再错过任何重要瞬间！

## 🌟 核心特性
- **全场景覆盖**：支持工作会议、作业提交、医院挂号、吃药复健等各类生活琐事。
- **自然语言解析**：直接对机器人说“明天下午三点吃降压药”或“周五晚上八点打本”，自动提取时间、事项并入库。
- **分级提醒机制**：
  - **前一天 20:00**：次日行程大纲晨报。
  - **前 30 分钟**：即将开始预警提醒。
  - **前 5 分钟**：马上开始紧急红色警报。
- **跨平台多渠道支持**：
  - **Telegram (海外推荐)**：无缝接入，轻量稳定。
  - **飞书 (国内推荐)**：支持图文 OCR、富文本卡片推送。

---

## 🚀 极简一键部署 (本地小白版)

无论你是 Windows、Mac 还是 Linux，无需任何复杂配置：

1. **环境准备**：请确保你的电脑已经安装了 `Python 3.10+`。
2. **复制配置**：将目录下的 `.env.example` 复制一份并重命名为 `.env`。
3. **填入 Token**：用记事本打开 `.env`，填入你的机器人渠道配置（如 Telegram Token）以及大模型配置。系统兼容任何提供 OpenAI 格式接口的大模型，你可以参考以下常用配置：
   - **Kimi (月之暗面)**：
     ```env
     LLM_API_KEY="sk-..."
     LLM_API_URL="https://api.moonshot.cn/v1/chat/completions"
     LLM_MODEL="moonshot-v1-8k"
     ```
   - **DeepSeek (深度求索)**：
     ```env
     LLM_API_KEY="sk-..."
     LLM_API_URL="https://api.deepseek.com/chat/completions"
     LLM_MODEL="deepseek-chat"
     ```
   - **OpenAI (ChatGPT)**：
     ```env
     LLM_API_KEY="sk-..."
     LLM_API_URL="https://api.openai.com/v1/chat/completions"
     LLM_MODEL="gpt-4o-mini"
     ```
4. **一键启动**：
   - **Windows 用户**：双击运行 `start.bat`。
   - **Mac 用户**：在 Finder 中双击 `start_mac.command`。*（首次运行：右键 → 打开 → 打开）*
   - **Linux 用户**：在终端运行 `bash start.sh`。

系统将自动创建虚拟环境、安装所需依赖并启动机器人！

---

## 📱 手机部署

### Android 安卓（通过 Termux）✅
你的安卓手机可以 24/7 运行日程管家：

```bash
# 1. 从 F-Droid 安装 Termux（不是 Play Store）
#    https://f-droid.org/packages/com.termux/

# 2. 安装 Python 环境
pkg update && pkg upgrade
pkg install python git

# 3. 克隆并配置
git clone https://github.com/YOUR_USER/schedule-butler.git
cd schedule-butler
cp .env.example .env
nano .env   # 填入你的 Token

# 4. 启动
bash start.sh

# 5. （可选）关闭 Termux 后保持运行
pkg install termux-services
# 然后用：nohup bash start.sh &
```

> 💡 **提示**：为防止安卓后台杀死 Termux，请到 **设置 → 电池 → Termux → 不受限制** 关闭省电优化。

### iPhone / iPad ❌
iOS 不允许后台运行 Python。替代方案：
- 用云服务器部署（如 5美元/月的 VPS），手机用 Telegram 收消息。
- 在家里电脑/Mac 上运行，手机用 Telegram 访问。

---

## 🛠️ Docker 部署 (极客推荐)
如果你喜欢使用 Docker 保持环境纯净：
```bash
docker-compose up -d
```

---

## 📝 支持的指令
| 指令 | 功能 | 消耗 Token？ |
|------|---------|:-----------:|
| *（任何含时间的文字）* | 自然语言录入日程 | ✅ 是 |
| `待办` | 查看未来 7 天所有待办 | ❌ 否 |
| `今日日程` / `今天日程` | 查看当天安排 | ❌ 否 |
| `本周日程` | 查看本周日程 | ❌ 否 |
| `删除 1` | 取消 ID 为 1 的日程 | ❌ 否 |
| `修改 1 时间为8点` | 自然语言修改日程 | ✅ 是 |
| `帮助` / `指南` | 显示使用指南 | ❌ 否 |

## 💡 极致省 Token 架构

日程管家的设计理念是**极致节约 Token**。所有操作中，**仅有 2 种场景消耗大模型 Token**：

1. **录入日程** — 大模型从你的自然语言消息中提取结构化数据（时间、标题、地点等），*每条日程仅调用一次*。
2. **修改日程** — 大模型解析你的修改意图（如「改时间为8点」），*每次修改仅调用一次*。

其余所有操作 — 查看待办、删除日程、定时提醒、每日简报 — 均基于**纯规则引擎 + 本地数据库查询**，零 API 调用。这意味着你可以一天查询几百次日程，不花一分钱 Token。

---

## 🤖 开源/本地模型支持

日程管家完全兼容通过 [Ollama](https://ollama.com)、[LM Studio](https://lmstudio.ai) 或任何 OpenAI 兼容 API 服务器本地部署的开源模型。

### 推荐模型
| 模型 | 参数量 | 质量 | 说明 |
|------|------|:----:|------|
| **Gemma 3 27B** | 27B | ⭐⭐⭐ | 最佳质量，需 16GB+ 显存 |
| **Gemma 3 14B** | 14B | ⭐⭐⭐ | 优秀，8GB+ 显存可跑 |
| **Qwen 2.5 14B** | 14B | ⭐⭐⭐ | 中英文双强 |
| **Gemma 3 7B** | 7B | ⭐⭐ | 大多数任务可用，偶尔丢字段 |
| **Qwen 2.5 7B** | 7B | ⭐⭐ | 中英双语稳定 |
| **Gemma 3 4B** | 4B | ⭐ | 可跑在手机（Android/Termux），建议英文使用 |
| **Gemma 3 1B** | 1B | ❌ | 太小，无法稳定输出结构化 JSON |

### Ollama 配置示例
```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 拉取模型
ollama pull gemma3:7b

# 自动在 localhost:11434 启动 OpenAI 兼容服务
```

然后配置 `.env`：
```env
LLM_API_KEY="ollama"
LLM_API_URL="http://localhost:11434/v1/chat/completions"
LLM_MODEL="gemma3:7b"
```

快来打造属于你的全能生活私人管家吧！
