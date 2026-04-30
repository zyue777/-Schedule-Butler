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
   - **Windows Users**: Double-click `start.bat`.
   - **Mac/Linux Users**: Run `bash start.sh` in your terminal.

The script will automatically create a virtual environment, install necessary dependencies, and start the bot!

---

## 🛠️ Docker Deployment (For Geeks)
If you prefer using Docker to keep your environment clean:
```bash
docker-compose up -d
```

---

## 📝 Supported Commands
- `Today's schedule` / `Today`: View all arrangements for the current day.
- `This week`: View your upcoming tasks for the week.
- `Delete 1`: Delete the scheduled event with ID 1.
- `Change time of 1 to 8 AM tomorrow`: Modify an existing schedule via natural language.

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
   - **Mac/Linux 用户**：在终端运行 `bash start.sh`。

系统将自动创建虚拟环境、安装所需依赖并启动机器人！

---

## 🛠️ Docker 部署 (极客推荐)
如果你喜欢使用 Docker 保持环境纯净：
```bash
docker-compose up -d
```

---

## 📝 支持的指令
- `今日日程` / `今天日程`：查看当天的所有安排。
- `本周日程`：查看未来一周的待办。
- `删除 1`：删除 ID 为 1 的日程安排。
- `修改 1 时间为明早8点`：通过自然语言修改已有的行程。

快来打造属于你的全能生活私人管家吧！
