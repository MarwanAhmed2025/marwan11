import os
from telethon import TelegramClient, events
API_ID=int(os.getenv('API_ID'))
API_HASH=os.getenv('API_HASH')
BOT_TOKEN=os.getenv('BOT_TOKEN')
client=TelegramClient('s',API_ID,API_HASH).start(bot_token=BOT_TOKEN)
@client.on(events.NewMessage(pattern='/start'))
async def s(e):await e.reply("ok")
client.run_until_disconnected()