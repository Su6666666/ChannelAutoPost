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
    MONGO_URI = "mongodb+srv://SGBACKUP:SGBACKUP@cluster0.qwvxwgs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
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

        # ১:১ ম্যাপিং লজিক যোগ করা হয়েছে
        try:
            # সোর্স চ্যানেলের ইনডেক্স খুঁজে বের করা (যেমন: ১ নম্বর না ২ নম্বর)
            source_index = frm.index(event.chat_id)
            # সেই ইনডেক্স অনুযায়ী টার্গেট চ্যানেল সেট করা
            target_channel = tochnls[source_index]
        except (ValueError, IndexError):
            # যদি ম্যাপিং না পাওয়া যায় তবে প্রসেস হবে না
            return

        try:
            if event.poll:
                return
            
            # ফাইলের আসল নাম খুঁজে বের করা
            file_name = event.file.name if event.file else None
            
            if file_name:
                # যদি ফাইল থাকে, তবে অরিজিনাল ফাইল নেম ক্যাপশন হিসেবে যাবে
                await datgbot.send_file(target_channel, event.message.media, caption=file_name)
            else:
                # যদি শুধু টেক্সট মেসেজ হয়, তবে যা আছে তাই কপি হবে
                await datgbot.send_message(target_channel, event.message)
            
            # ১.৫ সেকেন্ড বিরতি (সিরিয়াল ঠিক রাখতে)
            await asyncio.sleep(1.5) 
            
        except Exception as exc:
            log.error(f"Error sending to {target_channel}: {exc}")
            if "flood" in str(exc).lower():
                await asyncio.sleep(20)

        # মেসেজটি সফলভাবে পাঠানো হলে ডাটাবেসে সেভ করা
        await collection.insert_one({"msg_id": event.id, "chat_id": event.chat_id})

log.info("Bot has started with MongoDB Queue Logic and Mapping.")
datgbot.run_until_disconnected()
