# 🚀 Channel Auto-Post Bot (Advanced Sequential Mapping)

A powerful Telegram bot designed to automatically forward posts or files from one or multiple source channels to specific target channels. It is optimized for high-volume file transfers, ensuring that even if 100+ files are sent at once, they are posted in the exact sequential order.

## ✨ Key Features

* **1:1 Channel Mapping:** Supports multiple source and target channels simultaneously. Posts from the first source go to the first target, second to second, and so on (e.g., A+ -> B+, A- -> B-).
* **Sequential Queue:** Utilizes `asyncio.Lock` and `MongoDB` to ensure all messages are processed and posted in the correct serial order without any mixing.
* **Original Filename Restoration:** Automatically ignores source captions and sets the **Original Filename** (e.g., `movie.mkv`) as the new caption for the forwarded file.
* **Duplicate Protection:** Powered by MongoDB to track processed message IDs and prevent the same file from being forwarded twice.
* **Anti-Flood System:** Features a built-in 1.5-second delay between posts to comply with Telegram's limits and prevent bot bans.

---

## 🛠 Configuration & Environment Variables

Set the following variables in your deployment platform (Koyeb, Heroku, etc.):

| Variable | Description | Example |
| :--- | :--- | :--- |
| `APP_ID` | Your Telegram API ID | `123456` |
| `API_HASH` | Your Telegram API Hash | `abcdef123456...` |
| `BOT_TOKEN` | Token from @BotFather | `1234:abcd...` |
| `FROM_CHANNEL` | Source Channel IDs (Separated by Space) | `-100111 -100222` |
| `TO_CHANNEL` | Target Channel IDs (In the same order) | `-100333 -100444` |
| `MONGO_URI` | Your MongoDB Connection String | `mongodb+srv://...` |

> **Note:** Ensure the number of IDs in `FROM_CHANNEL` matches the number of IDs in `TO_CHANNEL`.

---

## 🚀 How to Deploy

1.  Clone or fork this repository.
2.  Set your Environment Variables in your hosting provider.
3.  Ensure all dependencies are listed in `requirements.txt`.
4.  Run the bot using `python3 bot.py`.

## 📦 Requirements
* Telethon
* Motor (Async MongoDB driver)
* Pymongo
* Python-decouple

---
**Maintained by:** (https://t.me/Sgbackup)  
Developed for high-volume file management with perfect sequencing. 🎯
