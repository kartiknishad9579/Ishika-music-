import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from pytgcalls.exceptions import NoActiveGroupCall, GroupCallNotFound
import yt_dlp
from PIL import Image, ImageDraw, ImageFont
from config import *
from tts import tts

app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
pytgcalls = PyTgCalls(app) # Bot se hi chalega

queue = {}
CHATS = set() # Broadcast ke liye

def yt_search(query):
    try:
        ydl_opts = {"format": "bestaudio", "noplaylist": True, "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
            return info["url"], info["title"]
    except:
        return None, None

async def create_welcome_card(user, chat):
    img = Image.new("RGB", (800, 500), "#C77DFF")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((320, 20), "Welcome!", fill="white", font=font)
    draw.rectangle([30, 70, 500, 110], outline="white", width=2)
    draw.text((40, 80), f"Name : {user.first_name}", fill="white", font=font)
    draw.rectangle([30, 120, 500, 160], outline="white", width=2)
    draw.text((40, 130), f"ID : {user.id}", fill="white", font=font)
    draw.rectangle([30, 170, 500, 210], outline="white", width=2)
    username = f"@{user.username}" if user.username else "No Username"
    draw.text((40, 180), f"Username : {username}", fill="white", font=font)
    draw.ellipse([550, 70, 770, 290], fill="#7B2CBF")
    draw.text((640, 160), "🍸", fill="yellow")
    y = 250
    draw.text((50, y), f"✦ WELCOME TO ✦", fill="white")
    draw.text((50, y+30), f"{chat.title.upper()}", fill="white")
    draw.text((50, y+70), f"➤ NAME ✦ {user.first_name}", fill="white")
    draw.text((50, y+100), f"➤ ID ✦ {user.id}", fill="white")
    draw.text((50, y+130), f"➤ USERNAME ✦ {username}", fill="white")
    draw.text((50, y+160), f"➤ TOTAL MEMBERS ✦ {chat.members_count}", fill="white")
    draw.text((280, y+200), f"Developed By OFFICIAL RAJ", fill="#FFC6FF")
    file_name = f"welcome_{user.id}.png"
    img.save(file_name)
    return file_name

@app.on_message(filters.command("start") & filters.private)
async def start(_, message: Message):
    user = await app.get_me()
    caption = f"**Hey {message.from_user.first_name}** ❗\n**This is {user.first_name}** ⭐\n\n🎧 **Ready To Feel The Music** 🐘\n\n➡️ `/play song name`\n➡️ `/skip`\n➡️ `/stop`\n➡️ `/broadcast` - Reply to msg"
    await message.reply_text(caption, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 ADD ME", url=f"https://t.me/{user.username}?startgroup=true")],
        [InlineKeyboardButton("👮 OWNER", url=f"tg://user?id={OWNER_ID}")]
    ]))

@app.on_message(filters.new_chat_members & filters.group)
async def welcome_both(_, message: Message):
    chat = await app.get_chat(message.chat.id)
    chat_id = message.chat.id
    CHATS.add(chat_id)
    bot_username = (await app.get_me()).username
    for new_user in message.new_chat_members:
        name = new_user.first_name
        card = await create_welcome_card(new_user, chat)
        username = f"@{new_user.username}" if new_user.username else 'None'
        caption = f"✦━━━◆ WELCOME TO ◆━━━✦\n◆ {chat.title.upper()} ◆\n\n➤ NAME ✦ {new_user.first_name}\n➤ ID ✦ `{new_user.id}`\n➤ USERNAME ✦ {username}\n➤ TOTAL MEMBERS ✦ {chat.members_count}\n\n✦━━━◆━━━✦━━━◆━━━✦"
        buttons = [
            [InlineKeyboardButton("👋 VIEW MEMBER", url=f"tg://user?id={new_user.id}")],
            [
                InlineKeyboardButton("📢 INVITE", url=f"https://t.me/{chat.username}") if chat.username
                else InlineKeyboardButton("📢 GROUP", url=f"https://t.me/c/{str(chat.id)[4:]}"),
                InlineKeyboardButton("💜 KIDNAP ME", url=f"tg://user?id={new_user.id}")
            ],
            [
                InlineKeyboardButton("🎵 PLAY", url=f"https://t.me/{bot_username}?start"),
                InlineKeyboardButton("⏭️ SKIP", callback_data="skip"),
                InlineKeyboardButton("⏹️ STOP", callback_data="stop")
            ],
            [
                InlineKeyboardButton("📊 STATS", callback_data="stats"),
                InlineKeyboardButton("⚡ DASHBOARD", callback_data="dashboard"),
                InlineKeyboardButton("🌐 LANG", callback_data="lang")
            ],
            [
                InlineKeyboardButton("👮 OWNER", url=f"tg://user?id={OWNER_ID}"),
                InlineKeyboardButton("📞 SUPPORT", url=SUPPORT_LINK),
                InlineKeyboardButton("📢 CHANNEL", url=CHANNEL_LINK)
            ],
            [
                InlineKeyboardButton("😂 MEMES", callback_data="memes"),
                InlineKeyboardButton("🎁 GIVEAWAY", callback_data="giveaway"),
                InlineKeyboardButton("❤️ REACT", callback_data="react")
            ]
        ]
        await message.reply_photo(photo=card, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
        os.remove(card)
        text = f"Welcome {name} to {chat.title}"
        file = tts(text, f"welcome_tts_{new_user.id}")
        try:
            await pytgcalls.join_group_call(chat_id, AudioPiped(file))
            await asyncio.sleep(4)
            await pytgcalls.leave_group_call(chat_id)
        except Exception:
            pass
        if os.path.exists(file): os.remove(file)

@app.on_message(filters.command("play") & filters.group)
async def play(_, message: Message):
    if len(message.command) < 2: return await message.reply("**Example:** `/play raatan lambiyan`")
    query = message.text.split(None, 1)[1]
    msg = await message.reply(f"**Searching...** `{query}`")
    url, title = yt_search(query)
    if not url:
        return await msg.edit("**Gaana nahi mila** ❌\nKoi aur naam try karo")
    chat_id = message.chat.id
    if chat_id in queue:
        queue[chat_id].append([title, url])
        return await msg.edit(f"**Added to Queue:** {title}")
    queue[chat_id] = [[title, url]]
    try:
        await pytgcalls.join_group_call(chat_id, AudioPiped(url))
        await msg.edit(f"**Now Playing:** {title}")
    except NoActiveGroupCall:
        await msg.edit("**VC On nahi hai** ❌\nPehle Voice Chat start karo")
    except Exception as e:
        await msg.edit(f"**Error:** {e}")

@app.on_message(filters.command("skip") & filters.group)
async def skip(_, message: Message):
    chat_id = message.chat.id
    if chat_id not in queue or len(queue[chat_id]) < 2: return await message.reply("**Queue khali hai** ⏭️")
    queue[chat_id].pop(0)
    title, url = queue[chat_id][0]
    try:
        await pytgcalls.change_stream(chat_id, AudioPiped(url))
        await message.reply(f"**Skipped. Now Playing:** {title}")
    except GroupCallNotFound:
        await message.reply("**VC me hu hi nahi** ❌")

@app.on_message(filters.command("stop") & filters.group)
async def stop(_, message: Message):
    chat_id = message.chat.id
    if chat_id in queue: queue.pop(chat_id)
    try:
        await pytgcalls.leave_group_call(chat_id)
        await message.reply("**Stopped and Left VC** ⏹️")
    except GroupCallNotFound:
        await message.reply("**VC me tha hi nahi**")

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(_, message: Message):
    if not message.reply_to_message:
        return await message.reply("**Reply karke /broadcast karo**")
    msg = await message.reply("**Broadcasting...**")
    sent = 0
    fail = 0
    for chat_id in list(CHATS):
        try:
            await message.reply_to_message.copy(chat_id)
            sent += 1
            await asyncio.sleep(0.5)
        except: fail += 1
    await msg.edit(f"**Broadcast Complete**\n\n✅ Sent: `{sent}`\n❌ Failed: `{fail}`")

@app.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    if query.data == "skip":
        await skip(client, query.message)
    elif query.data == "stop":
        await stop(client, query.message)
    elif query.data == "stats":
        await query.answer(f"Total Groups: {len(CHATS)}")
    elif query.data == "dashboard":
        await query.answer("Dashboard: Use /play to start")
    elif query.data == "lang":
        await query.answer("Language: Hindi/English")
    elif query.data == "memes":
        await query.answer("Memes Coming Soon 😂")
    elif query.data == "giveaway":
        await query.answer("No Giveaway Active")
    elif query.data == "react":
        await query.answer("❤️ Thanks for reacting!")

@pytgcalls.on_stream_end()
async def on_stream_end(client, update):
    chat_id = update.chat_id
    if chat_id in queue and len(queue[chat_id]) > 1:
        queue[chat_id].pop(0)
        title, url = queue[chat_id][0]
        await pytgcalls.change_stream(chat_id, AudioPiped(url))

print("Music Bot Started...")
pytgcalls.start()
app.run()
