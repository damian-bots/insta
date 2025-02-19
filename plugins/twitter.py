from pyrogram import filters, Client as Mbot
from bot import LOG_GROUP, DUMP_GROUP
import os
import asyncio
import traceback
import requests
import bs4
import re

API_URL = "https://twitsave.com/info?url="


async def fetch_twitter_video(url):
    """Fetch the highest quality Twitter/X video URL using TwitSave API."""
    try:
        response = requests.get(API_URL + url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data, status code: {response.status_code}")

        soup = bs4.BeautifulSoup(response.text, "html.parser")

        # Extract highest quality video URL
        download_button = soup.find("div", class_="origin-top-right")
        quality_buttons = download_button.find_all("a") if download_button else []

        if not quality_buttons:
            raise Exception("No video found in the provided link.")

        video_url = quality_buttons[0].get("href")  # Highest quality

        # Extract clean filename
        file_name_tag = soup.find("div", class_="leading-tight")
        file_name = file_name_tag.find("p", class_="m-2").text if file_name_tag else "twitter_video"

        file_name = re.sub(r"[^a-zA-Z0-9]+", ' ', file_name).strip() + ".mp4"

        return video_url, file_name

    except Exception as e:
        print(f"Error fetching video: {e}")
        return None, None


@Mbot.on_message(filters.regex(r'https?://.*twitter[^\s]+') & filters.incoming |
                 filters.regex(r'https?://(?:www\.)?x\.com/\S+') & filters.incoming, group=-5)
async def twitter_handler(Mbot, message):
    try:
        link = message.matches[0].group(0)

        # Convert Twitter/X links to normal format
        if "x.com" in link:
            link = link.replace("x.com", "twitter.com")

        processing_msg = await message.reply_sticker("CAACAgIAAxkBATWhF2Qz1Y-FKIKqlw88oYgN8N82FtC8AAJnAAPb234AAT3fFO9hR5GfHgQ")

        # Fetch video URL using API
        video_url, file_name = await fetch_twitter_video(link)

        if not video_url:
            await message.reply("❌ **Error:** Could not fetch video. The link might be invalid or private.")
            return

        # Try sending the video directly
        try:
            dump_file = await message.reply_video(video_url, caption="Thank you for using - @DeadlineReelbot")
        except Exception as e:
            print(f"Error sending video directly: {e}")
            await message.reply_text(f"Here is the media link:\n{video_url}")

        # Store media in dump group
        if DUMP_GROUP and "dump_file" in locals():
            await dump_file.copy(DUMP_GROUP)

    except Exception as e:
        print(f"Unexpected Error: {e}")
        if LOG_GROUP:
            await Mbot.send_message(LOG_GROUP, f"Twitter Fetch Error: {e}\nChat ID: {message.chat.id}")
            await Mbot.send_message(LOG_GROUP, traceback.format_exc())

    finally:
        await processing_msg.delete()
        await message.reply("Check out @spotifyXMusicBot 🎵 and @DeadlineTech 📢\nSupport us with /donate to maintain this project!")
