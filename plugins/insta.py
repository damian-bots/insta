from pyrogram import filters, Client as Mbot
import requests, re, asyncio, traceback
from bot import LOG_GROUP, DUMP_GROUP

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/x-www-form-urlencoded",
    "X-Requested-With": "XMLHttpRequest",
}

API_URL = "https://snapinsta.io/api/ajaxSearch"

@Mbot.on_message(filters.regex(r'https?://.*instagram[^\s]+') & filters.incoming)
async def link_handler(client, message):
    link = message.matches[0].group(0)
    m = await message.reply_sticker("CAACAgIAAxkBATWhF2Qz1Y-FKIKqlw88oYgN8N82FtC8AAJnAAPb234AAT3fFO9hR5GfHgQ")

    try:
        response = requests.post(
            API_URL, 
            data={"q": link, "t": "media", "lang": "en"}, 
            headers=HEADERS, 
            timeout=10
        )

        if response.ok:
            res = response.json()
            video_urls = re.findall(r'href="(https?://[^"]+)"', res.get('data', ''))

            if video_urls:
                for video_url in video_urls:
                    try:
                        dump_file = await message.reply_video(video_url, caption="Thank you for using - @DeadlineReelbot 📢")
                        await asyncio.sleep(1)
                    except Exception:
                        pass
            else:
                await message.reply("⚠️ No video found! Please check the link or try again later.")
        else:
            raise Exception("API request failed.")

    except requests.exceptions.RequestException:
        await message.reply("⚠️ Error: Unable to connect to SnapInsta. Try again later.")

    except Exception as e:
        if LOG_GROUP:
            await client.send_message(LOG_GROUP, f"Instagram Download Error: {e}\nLink: {link}")
            await client.send_message(LOG_GROUP, traceback.format_exc())
        await message.reply("⚠️ 400: Unable to retrieve the video. Please report to @DeadlineTechOwner or @DeadlineTechsupport.")

    finally:
        await m.delete()
        if 'dump_file' in locals() and dump_file:
            await dump_file.copy(DUMP_GROUP)
        await message.reply("🔔 Check out @DeadlineTech 📢\n💖 Support us with /donate to maintain this project.")
