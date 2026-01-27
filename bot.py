import logging
import asyncio
import re
from telethon import TelegramClient, events, Button
from decouple import config
from database import Database

# লগিং কনফিগারেশন
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(message)s")
log = logging.getLogger("ChannelAutoPost")

try:
    API_ID = config("APP_ID", cast=int)
    API_HASH = config("API_HASH")
    BOT_TOKEN = config("BOT_TOKEN")
    MONGO_URI = config("MONGO_URI")
    ADMIN_ID = config("ADMIN_ID", cast=int)
    
    bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
    db = Database(MONGO_URI)
except Exception as e:
    log.error(f"Error: {e}")
    exit()

# ১. লিংক ও ইউজারনেম ক্লিনার (Regex)
def clean_text(text):
    if not text: return ""
    # সব ধরণের URL এবং @username মুছে ফেলা হবে
    text = re.sub(r'http\S+|www\S+|t\.me\/\S+|@\w+', '', text)
    return text.strip()

# ২. সিকুয়েন্স মেইনটেইনার (Queue)
post_queue = asyncio.Queue()

async def worker():
    while True:
        source_id, event, dest_id = await post_queue.get()
        try:
            caption = clean_text(event.text)
            # মিলিসেকেন্ড ডিলে সহ পোস্ট করা
            if event.media:
                await bot.send_file(dest_id, event.media, caption=caption)
            else:
                await bot.send_message(dest_id, caption)
            await asyncio.sleep(0.5) # ৫০০ মিলিসেকেন্ড গ্যাপ
        except Exception as e:
            log.error(f"Post Error: {e}")
        finally:
            post_queue.task_done()

# ৩. কমান্ড হ্যান্ডলার (In-Bot Control)
@bot.on(events.NewMessage(pattern="/add", from_users=ADMIN_ID))
async def add_map(event):
    args = event.text.split()
    if len(args) == 3:
        await db.add_mapping(int(args[1]), int(args[2]))
        await event.reply("✅ Mapping Added! Now I will forward from source to dest.")
    else:
        await event.reply("❌ Use: `/add [Source_ID] [Dest_ID]`")

@bot.on(events.NewMessage(incoming=True))
async def handle_posts(event):
    if event.is_channel:
        dest_id = await db.get_mapping(event.chat_id)
        if dest_id:
            await post_queue.put((event.chat_id, event, dest_id))

async def run_bot():
    asyncio.create_task(worker())
    await bot.run_until_disconnected()

if __name__ == "__main__":
    bot.loop.run_until_complete(run_bot())
