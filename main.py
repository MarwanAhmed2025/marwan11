# -*- coding: utf-8 -*-
import os
from telethon import TelegramClient, events

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

print("Bot is starting...")
client = TelegramClient('session_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(pattern=r'\.help'))
async def help_cmd(event):
    await event.reply("Bot is online 24/7")

@client.on(events.NewMessage(pattern=r'\.start'))
async def start_cmd(event):
    await event.reply("Hello! Your bot is working")

print("Bot is connected")
client.run_until_disconnected()