from pyrogram import filters, Client as Mbot
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import bs4, requests
from bot import DUMP_GROUP
from apscheduler.schedulers.background import BackgroundScheduler
from sys import executable
from os import sys, execl, environ

# if you are using a service like Heroku, after restart it changes IP which avoids IP blocking
# Also restart when an unknown error occurs and the bot is idle
RESTART_ON = environ.get('RESTART_ON')

def restart():
    execl(executable, executable, "bot.py")

if RESTART_ON:
    scheduler = BackgroundScheduler()
    scheduler.add_job(restart, "interval", hours=6)
    scheduler.start()

def get_inline_buttons():
    """Generate inline buttons for updates and support."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Updates 📢", url="https://t.me/DeadlineTech")],
        [InlineKeyboardButton("Support 💬", url="https://t.me/DeadlineTechsupport")]
    ]) 

def get_inline():
    """Generate inline buttons for updates and support."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Donate Stars ⭐", url="https://t.me/+akVZj1IYX_NmZjg1")]
    ])

@Mbot.on_message(filters.incoming & filters.private, group=-1)
async def monitor(Mbot, message):
    if DUMP_GROUP:
        await message.forward(DUMP_GROUP)

@Mbot.on_message(filters.command("start") & filters.incoming)
async def start(Mbot, message):
    # Sending a more detailed welcome message for each platform
    welcome_message = (
        f"Hello 👋👋 {message.from_user.mention()},\n\n"
        "I am Deadline Reel bot that can download content from the following platforms:\n\n"
        "🔹 **Instagram Reels**: Send me Instagram Reel links, and I’ll download them for you!\n"
        "🔹 **YouTube Shorts**: Share any YouTube Shorts link, and I’ll fetch the video for you!\n"
        "🔹 **Facebook Reels**: Send me a Facebook Reel link, and I’ll get the video for you!\n"
        "🔹 **TikTok Shorts**: Just drop a TikTok link, and I'll help you download the video!\n"
        "🔹 **Twitter Post**: Send me Twitter post links (including media), and I’ll download them instantly!\n\n"
        "Just paste a link, and I'll take care of the rest!\n\n"
        "Use the buttons below to stay updated or reach out for support."
    )
    
    # Sending the message with inline buttons
    await message.reply(
        welcome_message,
        reply_markup=get_inline_buttons()
    )

@Mbot.on_message(filters.command("help") & filters.incoming)
async def help(Mbot, message):
    # Sending a reply with inline buttons
    await message.reply(
        "This is a user-friendly bot. You can simply send your Instagram reel and post links here. For example:\n\n"
        "`https://www.instagram.com/reel/CZqWDGODoov/?igshid=MzRlODBiNWFlZA==`\n"
        "`post:` `https://www.instagram.com/reel/CuCTtORJbDj/?igshid=MzRlODBiNWFlZA==`",
        reply_markup=get_inline_buttons()
    )

@Mbot.on_message(filters.command("donate") & filters.command("Donate") & filters.incoming)
async def donate(_, message):
    # Sending a reply with inline buttons
    await message.reply_text(
        "Donate 🍪 - \n𝗨𝗣𝗜 - `tusar0925@fam` \n𝗕𝗶𝗮𝗻𝗮𝗻𝗰𝗲 𝗜𝗱 - `1018816596`",
        reply_markup=get_inline()
    )
