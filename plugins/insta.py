from pyrogram import filters, Client as Mbot
import bs4, requests, re, asyncio, os, random, traceback
from bot import LOG_GROUP, DUMP_GROUP

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://saveig.app",
    "Referer": "https://saveig.app/en",
}

@Mbot.on_message(filters.regex(r'https?://.*instagram[^\s]+') & filters.incoming)
async def link_handler(client, message):
    link = message.matches[0].group(0)
    m = await message.reply_sticker("CAACAgIAAxkBATWhF2Qz1Y-FKIKqlw88oYgN8N82FtC8AAJnAAPb234AAT3fFO9hR5GfHgQ")
    
    try:
        url = link.replace("instagram.com", "ddinstagram.com").replace("==", "%3D%3D")
        dump_file = await message.reply_video(url, caption="Thank you for using - @DeadlineReelbot 📢")
        if dump_file:
            await dump_file.forward(DUMP_GROUP)
        await m.delete()
        return
    except Exception:
        pass  # If ddinstagram fails, fall back to other methods
    
    try:
        if "/reel/" in link or "/p/" in link or "stories" in link:
            response = requests.post("https://saveig.app/api/ajaxSearch", 
                                     data={"q": link, "t": "media", "lang": "en"}, 
                                     headers=HEADERS, timeout=10)
            
            if response.ok:
                res = response.json()
                meta_links = re.findall(r'href="(https?://[^"]+)"', res['data'])
                
                if meta_links:
                    for meta_link in meta_links:
                        try:
                            dump_file = await message.reply_video(meta_link, caption="Thank you for using - @DeadlineReelbot 📢")
                            await asyncio.sleep(1)
                        except Exception:
                            pass
                else:
                    await message.reply("Failed to retrieve video. Please check the link.")
            else:
                raise Exception("saveig.app request failed.")
    except requests.exceptions.RequestException:
        await message.reply("Error: Unable to connect to saveig.app. Try again later.")
    except Exception as e:
        if LOG_GROUP:
            await client.send_message(LOG_GROUP, f"Instagram Download Error: {e}\nLink: {link}")
            await client.send_message(LOG_GROUP, traceback.format_exc())
        await message.reply("400: Unable to retrieve the video. Please report to @DeadlineTechOwner or @DeadlineTechsupport.")
    
    finally:
        await m.delete()
        if 'dump_file' in locals() and dump_file:
            await dump_file.copy(DUMP_GROUP)
        await message.reply("Check out @DeadlineTech 📢\nPlease Support Us By /donate To Maintain This Project")
