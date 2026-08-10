import os
from telethon import TelegramClient, events

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

print("جاري تشغيل البوت...")
client = TelegramClient('session_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(pattern=r'\.help'))
async def help_cmd(event):
    await event.reply("✅ البوت شغال 24 ساعة بدون كود\nالاوامر:\n.help - لعرض الاوامر")

@client.on(events.NewMessage(pattern=r'\.start'))
async def start_cmd(event):
    await event.reply("اهلا! انا البوت بتاعك شغال")

print("✅ البوت شغال ومتصل")
client.run_until_disconnected()
