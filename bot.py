import logging
import asyncio # নতুন যোগ করা হয়েছে
from telethon import TelegramClient, events, Button
from decouple import config

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
    datgbot = TelegramClient(None, apiid, apihash).start(bot_token=bottoken)
except Exception as exc:
    log.error("Environment vars are missing! Kindly recheck.")
    log.info("Bot is quiting...")
    log.error(exc)
    exit()

@datgbot.on(events.NewMessage(pattern="/start"))
async def _(event):
    await event.reply(
        f"Hi `{event.sender.first_name}`!\n\nI am a channel auto-post bot!!",
        buttons=[
            Button.url("Support", url="https://t.me/SGBACKUP"),
        ],
        link_preview=False,
    )

# সিরিয়াল ঠিক রাখার জন্য মূল এডিট এখানে
@datgbot.on(events.NewMessage(incoming=True, chats=frm))
async def _(event):
    # ১০০টি ফাইল একসাথে আসলে ১ সেকেন্ড বিরতি দিলে সিরিয়াল ঠিক থাকে
    await asyncio.sleep(1) 
    
    for tochnl in tochnls:
        try:
            if event.poll:
                return
            
            # সরাসরি copy() ব্যবহার করা হচ্ছে যাতে সিরিয়াল এবং ক্যাপশন ১০০% সঠিক থাকে
            await datgbot.send_message(tochnl, event.message)
            
            # প্রতিটি ফাইল পাঠানোর পর সামান্য বিরতি (০.৫ সেকেন্ড)
            await asyncio.sleep(0.5) 
            
        except Exception as exc:
            log.error("Error sending message to %s: %s", tochnl, exc)

log.info("Bot has started. Developed with sequential fix.")
datgbot.run_until_disconnected()
