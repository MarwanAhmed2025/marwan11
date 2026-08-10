#!/usr/bin/env python3
import asyncio
import json
import os
from telethon import TelegramClient, events
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import Channel, InputPeerEmpty, User
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError

# ===== قراءة البيانات من المتغيرات =====
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
PHONE = os.getenv('PHONE')
# ========================================

SESSION_NAME = 'papalaoo_session'
LEFT_FILE = 'left_groups.json'
DOWNLOAD_PATH = 'downloads'
PREFIX = '.'

os.makedirs(DOWNLOAD_PATH, exist_ok=True)

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
known_groups = {}

if os.path.exists(LEFT_FILE):
    with open(LEFT_FILE, 'r', encoding='utf-8') as f:
        left_groups = json.load(f)
else:
    left_groups = []

async def save_left_groups():
    with open(LEFT_FILE, 'w', encoding='utf-8') as f:
        json.dump(left_groups, f, ensure_ascii=False, indent=2)

async def get_entity_safe(identifier):
    try: return await client.get_entity(identifier)
    except:
        result = await client(SearchRequest(q=identifier.replace('@',''), limit=1))
        return result.users[0] if result.users else None

async def get_my_groups():
    result = await client(GetDialogsRequest(offset_date=None, offset_id=0, offset_peer=InputPeerEmpty(), limit=200, hash=0))
    groups = []
    global known_groups
    known_groups = {}
    for chat in result.chats:
        if isinstance(chat, Channel):
            typ = "📢 قناة" if chat.broadcast else "👥 مجموعة"
            groups.append(f"{typ} **{chat.title}**\nID: `{chat.id}`")
            known_groups[chat.id] = chat.title
    return groups if groups else ["❌ ما انت عضو في اي مجموعة"]

async def get_user_groups(identifier):
    user = await get_entity_safe(identifier)
    if not user: return ["❌ اليوزر غير موجود"]
    await client.send_message('me', "🔍 جاري فحص المجموعات المشتركة...")
    user_groups = []
    for chat_id, title in known_groups.items():
        try:
            await client(GetParticipantRequest(channel=chat_id, participant=user.id))
            user_groups.append(f"✅ **{title}**\nID: `{chat_id}`")
            await asyncio.sleep(0.3)
        except UserNotParticipantError: continue
        except: continue
    if not user_groups: return [f"❌ **{user.first_name}** مش عضو في اي مجموعة مشتركة معاك"]
    return [f"📋 المجموعات المشتركة مع **{user.first_name}**:"] + user_groups

async def download_group_media(chat_id, limit):
    await client.send_message('me', f"📥 جاري تحميل اخر {limit} ميديا...")
    count = 0
    async for msg in client.iter_messages(chat_id, limit=limit):
        if msg.media:
            await msg.download_media(file=DOWNLOAD_PATH)
            count += 1
            await asyncio.sleep(0.5)
    return f"✅ تم تحميل {count} ملف في `{DOWNLOAD_PATH}`"

async def forward_all(source_id, target_id, limit):
    source = await get_entity_safe(source_id)
    target = await get_entity_safe(target_id)
    if not source or not target: return "❌ مصدر او هدف غير موجود"
    await client.send_message('me', f"⏩ جاري تحويل اخر {limit} رسالة...")
    count = 0
    async for msg in client.iter_messages(source_id, limit=limit):
        await msg.forward_to(target_id)
        count += 1
        await asyncio.sleep(1)
    return f"✅ تم تحويل {count} رسالة"

@client.on(events.ChatAction)
async def chat_action_handler(event):
    if event.user_left and event.user_id == (await client.get_me()).id:
        chat = await event.get_chat()
        if isinstance(chat, Channel):
            group_data = {"id": chat.id, "title": chat.title, "type": "قناة" if chat.broadcast else "مجموعة", "time": event.date.strftime("%Y-%m-%d %H:%M")}
            if group_data not in left_groups:
                left_groups.append(group_data)
                await save_left_groups()
                await client.send_message('me', f"📤 تم تسجيل المغادرة: **{chat.title}**")

@client.on(events.NewMessage(from_users='me', pattern=rf'\{PREFIX}(.*)'))
async def command_handler(event):
    cmd_full = event.pattern_match.group(1).strip()
    parts = cmd_full.split(' ')

    if cmd_full.startswith('search '):
        await event.reply("🔍 جاري البحث...")
        result = await client(SearchRequest(q=parts[1], limit=10))
        users = [f"{'🤖' if u.bot else '👤'} **{u.first_name}**\n@{u.username}\nID: `{u.id}`" for u in result.users]
        await event.reply("\n\n".join(users) if users else "❌ ما لقيت")

    elif cmd_full == 'groups':
        await event.reply("📋 جاري جلب مجموعاتك...")
        await event.reply("\n\n".join(await get_my_groups())[:4000])

    elif cmd_full.startswith('usergroups '):
        await event.reply("\n\n".join(await get_user_groups(parts[1]))[:4000])

    elif cmd_full.startswith('info '):
        user = await get_entity_safe(parts[1])
        if not user: await event.reply("❌ غير موجود"); return
        full = await client(GetFullUserRequest(user))
        await event.reply(f"**{user.first_name}**\n@{user.username}\nID: `{user.id}`\nBio: {full.about or 'لا يوجد'}")

    elif cmd_full.startswith('download_media '):
        try:
            chat_id = int(parts[1]); limit = int(parts[2]) if len(parts) > 2 else 20
            await event.reply(await download_group_media(chat_id, limit))
        except: await event.reply("❌ الاستخدام:.download_media group_id عدد")

    elif cmd_full.startswith('forward_all '):
        try:
            from_id = parts[1]; to_id = parts[2]; limit = int(parts[3]) if len(parts) > 3 else 20
            await event.reply(await forward_all(from_id, to_id, limit))
        except: await event.reply("❌ الاستخدام:.forward_all from_id to_id عدد")

    elif cmd_full == 'help':
        await event.reply(f"""
**Papalaoo Clone**
`.search اسم` `.groups` `.usergroups @user`
`.info @user` `.download_media id عدد`
`.forward_all from to عدد` `.help`
""")

async def main():
    await client.start(phone=PHONE)
    await get_my_groups()
    me = await client.get_me()
    print(f"✅ البوت شغال: {me.first_name}")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())