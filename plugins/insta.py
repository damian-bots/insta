from pyrogram import filters, Client as Mbot
import requests, re, asyncio, os, traceback, random
import bs4
from bot import LOG_GROUP, DUMP_GROUP

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/x-www-form-urlencoded",
    "X-Requested-With": "XMLHttpRequest",
}

INSTA_API = "https://www.instadownloader.co/api/ajaxSearch"

@Mbot.on_message(filters.regex(r'https?://.*instagram[^\s]+') & filters.incoming)
async def link_handler(client, message):
    link = message.matches[0].group(0)
    m = await message.reply_sticker("CAACAgIAAxkBATWhF2Qz1Y-FKIKqlw88oYgN8N82FtC8AAJnAAPb234AAT3fFO9hR5GfHgQ")

    try:
        # 1️⃣ Try ddinstagram first
        url = link.replace("instagram.com", "ddinstagram.com").replace("==", "%3D%3D")
        try:
            dump_file = await message.reply_video(url, caption="✅ Video Downloaded via @DeadlineReelbot 📢")
            await dump_file.forward(DUMP_GROUP)
            await m.delete()
            return
        except Exception:
            pass  # If ddinstagram fails, fall back to Insta API

        # 2️⃣ Use InstaDownloader API as a backup
        response = requests.post(INSTA_API, data={"q": link, "t": "media", "lang": "en"}, headers=HEADERS, timeout=10)
        if response.ok:
            res = response.json()
            video_urls = re.findall(r'href="(https?://[^"]+)"', res.get('data', ''))
            
            if video_urls:
                for video_url in video_urls:
                    try:
                        dump_file = await message.reply_video(video_url, caption="✅ Video Downloaded via @DeadlineReelbot 📢")
                        await asyncio.sleep(1)
                    except Exception:
                        pass
                await m.delete()
                return
            else:
                raise Exception("No video URLs found.")

        # 3️⃣ If API fails, try direct scraping (for reels)
        if "/reel/" in link or "/p/" in link:
            try:
                getdata = requests.get(link).text
                soup = bs4.BeautifulSoup(getdata, 'html.parser')
                meta_tag = soup.find('meta', attrs={'property': 'og:video'})
                if meta_tag:
                    video_url = meta_tag['content']
                    dump_file = await message.reply_video(video_url, caption="✅ Video Downloaded via @DeadlineReelbot 📢")
                    await dump_file.forward(DUMP_GROUP)
                    await m.delete()
                    return
            except Exception:
                pass

    except requests.exceptions.RequestException:
        await message.reply("⚠️ Unable to connect to Instagram downloader services. Please try again later.")

    except Exception as e:
        if LOG_GROUP:
            await client.send_message(LOG_GROUP, f"Instagram Download Error: {e}\nLink: {link}")
            await client.send_message(LOG_GROUP, traceback.format_exc())
        await message.reply("❌ Unable to retrieve the video. Please make sure the link is public.")

    finally:
        await m.delete()
        if 'dump_file' in locals() and dump_file:
            await dump_file.copy(DUMP_GROUP)
        await message.reply("🔔 Check out @DeadlineTech 📢\n💖 Support us with /donate to maintain this project.")
