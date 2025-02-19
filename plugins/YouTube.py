import os
from pyrogram import filters, Client as Mbot
from random import randint
from bot import LOG_GROUP, DUMP_GROUP
from yt_dlp import YoutubeDL
from requests import Session
import traceback
from shutil import rmtree

COOKIES_PATH = "cookies/cookies.txt"  # Define the cookies path

# YouTube download video function
async def ytdl_video(path, video_url):
    print(video_url)
    file = f"{path}/%(title)s.%(ext)s"
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
        "noplaylist": True,
        "nocheckcertificate": True,
        "outtmpl": file,
        "quiet": True,
        "addmetadata": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "cache-dir": "/tmp/",
        "cookiefile": COOKIES_PATH,  # Use cookiefile instead of browser cookies
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            video = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(video)
            print(filename)
            return filename
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None


async def ytdl_down(path, video_url):
    print(video_url)
    file = f"{path}/%(title)s"
    ydl_opts = {
        "format": "bestaudio",
        "noplaylist": True,
        "nocheckcertificate": True,
        "outtmpl": file,
        "quiet": True,
        "addmetadata": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "cache-dir": "/tmp/",
        "cookiefile": COOKIES_PATH,  # Use cookiefile instead of browser cookies
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "320"}
        ],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            video = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(video)
            return f"{filename}.mp3"
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None


# Get IDs for a video or playlist
async def getIds(video):
    ids = []
    with YoutubeDL({'quiet': True, 'cookiefile': COOKIES_PATH}) as ydl:
        info_dict = ydl.extract_info(video, download=False)
        try:
            info_dict = info_dict['entries']
            ids.extend([x.get('id'), x.get('playlist_index'), x.get('creator') or x.get('uploader'), x.get('title'), x.get('duration'), x.get('thumbnail')] for x in info_dict)
        except:
            ids.append([info_dict.get('id'), info_dict.get('playlist_index'), info_dict.get('creator') or info_dict.get('uploader'), info_dict.get('title'), info_dict.get('duration'), info_dict.get('thumbnail')])
    return ids


@Mbot.on_message(filters.regex(r'https?://.*youtube[^\s]+') & filters.incoming | filters.regex(r'(https?:\/\/(?:www\.)?youtu\.?be(?:\.com)?\/.*)') & filters.incoming)
async def download_youtube(Mbot, message):
    try:
        m = await message.reply_sticker("CAACAgIAAxkBATWhF2Qz1Y-FKIKqlw88oYgN8N82FtC8AAJnAAPb234AAT3fFO9hR5GfHgQ")
    except:
        pass
    link = message.matches[0].group(0)

    if "channel" in link or "/c/" in link:
        return await m.edit_text("**Channel** Download Not Available.")

    if "shorts" in link:
        try:
            randomdir = "/tmp/" + str(randint(1, 100000000))
            os.mkdir(randomdir)
            fileLink = await ytdl_video(randomdir, link)
            if fileLink:
                AForCopy = await message.reply_video(fileLink)
                if os.path.exists(randomdir):
                    rmtree(randomdir)
                await m.delete()
                if DUMP_GROUP:
                    await AForCopy.copy(DUMP_GROUP)
            else:
                await message.reply("Error: Could not download video.")
        except Exception as e:
            await m.delete()
            if LOG_GROUP:
                await Mbot.send_message(LOG_GROUP, f"YouTube Shorts {e} {link}")
            await message.reply("400: Sorry, Unable To Find It. Try another or report it to support.")
            print(traceback.format_exc())
            await Mbot.send_message(LOG_GROUP, traceback.format_exc())
        return

    try:
        if "music.youtube.com" in link:
            link = link.replace("music.youtube.com", "youtube.com")
        ids = await getIds(link)
        videoInPlaylist = len(ids)
        randomdir = "/tmp/" + str(randint(1, 100000000))
        os.mkdir(randomdir)

        for id in ids:
            link = f"https://youtu.be/{id[0]}"
            PForCopy = await message.reply_photo(f"https://i.ytimg.com/vi/{id[0]}/hqdefault.jpg", caption=f"🎧 Title : `{id[3]}`\n🎤 Artist : `{id[2]}`\n💽 Track No : `{id[1]}`\n💽 Total Track : `{videoInPlaylist}`")
            fileLink = await ytdl_down(randomdir, link)
            if fileLink:
                AForCopy = await message.reply_audio(fileLink, caption=f"[{id[3]}](https://youtu.be/{id[0]}) - {id[2]} Thank you for using - @DeadlineReelBot", title=id[3].replace("_", " "), performer=id[2], duration=id[4])
                if DUMP_GROUP:
                    await PForCopy.copy(DUMP_GROUP)
                    await AForCopy.copy(DUMP_GROUP)

        await m.delete()
        if os.path.exists(randomdir):
            rmtree(randomdir)
        await message.reply("Check out @DeadlineTech 📢 \nPlease Support Us By /donate To Maintain This Project")
    except Exception as e:
        print(e)
        if LOG_GROUP:
            await Mbot.send_message(LOG_GROUP, f"Youtube {e} {link}")
            await message.reply("400: Sorry, Unable To Find It. Try another or report it to support.")
            await Mbot.send_message(LOG_GROUP, traceback.format_exc())
