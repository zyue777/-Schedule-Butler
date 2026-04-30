# 📅 Schedule Butler

An **all-in-one cross-platform life and memory assistant**. Whether it's a business meeting, student classes, outdoor activities, or daily medication reminders, just send a simple message. The Schedule Butler will alert you at the critical moments so you never miss an important event again!

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
3. **Fill in Tokens**: Open `.env` with a text editor. Fill in your LLM Token (e.g., Kimi/Moonshot) and your bot channel configuration (e.g., Telegram Bot Token).
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
To view logs:
```bash
docker-compose logs -f
```

---

## 📝 Supported Commands
- `Today's schedule` / `Today`: View all arrangements for the current day.
- `This week`: View your upcoming tasks for the week.
- `Delete 1`: Delete the scheduled event with ID 1.
- `Change time of 1 to 8 AM tomorrow`: Modify an existing schedule via natural language.

Build your ultimate personal life butler today!
