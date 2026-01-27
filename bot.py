import logging
import asyncio
from telethon import TelegramClient, events, Button
from decouple import config
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(
    level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(message)s"
)
log = logging.getLogger("ChannelAutoPost")

log.info("Starting...")
try:
    apiid = config("APP_ID", cast=int)
    apihash = config("API_HASH")
    bottoken = config("BOT_TOKEN")
    frm = config("FROM_CHANNEL", cast=lambda x: [int(_) for _ in x.split(" ")])
    tochnls = config("TO_CHANNEL", cast=lambda x: [int(_) for _ in x.split(" ")])
    
    # আপনার দেওয়া MongoDB URI
    MONGO_URI = "mongodb+srv://SGBACKUP:SGBACKUP@cluster0.64jkmog.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    db_client = AsyncIOMotorClient(MONGO_URI)
    db = db_client.channel_bot
    collection = db.processed_msgs

    datgbot = TelegramClient(None, apiid, apihash).start(bot_token=bottoken)
except Exception as exc:
    log.error(f"Error starting bot: {exc}")
    exit()

# মেসেজ কিউ বা সারি মেইনটেইন করার জন্য একটি লক
queue_lock = asyncio.Lock()

@datgbot.on(events.NewMessage(pattern="/start"))
async def _(event):
    await event.reply("Bot is Active and Sequential Forwarding is ON!")

@datgbot.on(events.NewMessage(incoming=True, chats=frm))
async def _(event):
    # লক ব্যবহার করা হচ্ছে যাতে একটির পর একটি মেসেজ প্রসেস হয়
    async with queue_lock:
        # মেসেজটি ইতিমধ্যে প্রসেস হয়েছে কি না চেক করা (ডুপ্লিকেট এড়াতে)
        is_processed = await collection.find_one({"msg_id": event.id, "chat_id": event.chat_id})
        if is_processed:
            return

        for tochnl in tochnls:
            try:
                if event.poll:
                    return
                
                # হুবহু মেসেজটি কপি করে পাঠানো
                await datgbot.send_message(tochnl, event.message)
                
                # ১.৫ সেকেন্ড বিরতি (টেলিগ্রামের ফ্লাড লিমিট এবং সিরিয়াল ঠিক রাখতে এটিই সেরা)
                await asyncio.sleep(1.5) 
                
            except Exception as exc:
                log.error(f"Error sending to {tochnl}: {exc}")
                # যদি টেলিগ্রাম থেকে 'Flood Wait' এরর দেয়, তবে এটি বটকে কিছুক্ষণ থামিয়ে রাখবে
                if "flood" in str(exc).lower():
                    await asyncio.sleep(20)

        # মেসেজটি সফলভাবে পাঠানো হলে ডাটাবেসে সেভ করা
        await collection.insert_one({"msg_id": event.id, "chat_id": event.chat_id})

log.info("Bot has started with MongoDB Queue Logic.")
datgbot.run_until_disconnected()
