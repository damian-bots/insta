from pyrogram import filters, Client as Mbot
from bot import LOG_GROUP, DUMP_GROUP
import os, asyncio, traceback
import requests
import bs4


@Mbot.on_message(filters.regex(r'https?://.*twitter[^\s]+') & filters.incoming |
                 filters.regex(r'https?://(?:www\.)?x\.com/\S+') & filters.incoming, group=-5)
async def twitter_handler(Mbot, message):
    try:
        link = message.matches[0].group(0)

        # Convert Twitter/X links to alternative download service
        if "x.com" in link:
            link = link.replace("x.com", "fxtwitter.com")
        elif "twitter.com" in link:
            link = link.replace("twitter.com", "fxtwitter.com")

        # Send processing sticker
        processing_msg = await message.reply_sticker("CAACAgIAAxkBATWhF2Qz1Y-FKIKqlw88oYgN8N82FtC8AAJnAAPb234AAT3fFO9hR5GfHgQ")

        # Try sending video directly
        try:
            dump_file = await message.reply_video(link, caption="Thank you for using - @DeadlineReelbot")
        except Exception as e:
            print(f"Error sending video directly: {e}")

            # Attempt to fetch media manually
            try:
                response = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
                if response.status_code != 200:
                    raise Exception(f"Failed to fetch page, status code: {response.status_code}")

                soup = bs4.BeautifulSoup(response.text, "html.parser")

                # Find media URL (video > image)
                media_url = None
                meta_video = soup.find("meta", attrs={"property": "og:video"})
                meta_image = soup.find("meta", attrs={"property": "og:image"})

                if meta_video:
                    media_url = meta_video.get("content")
                elif meta_image:
                    media_url = meta_image.get("content")

                if not media_url:
                    raise Exception("No valid media found in metadata.")

                # Try sending the found media
                try:
                    dump_file = await message.reply_video(media_url, caption="Thank you for using - @DeadlineReelbot")
                except Exception as e:
                    print(f"Error sending extracted video: {e}")
                    await message.reply_text(f"Here is the media link:\n{media_url}")

            except Exception as e:
                print(f"Final Error: {e}")
                await message.reply("❌ **Error:** Invalid link or media is not available.")
                if LOG_GROUP:
                    await Mbot.send_message(LOG_GROUP, f"Twitter Fetch Error: {e}\nChat ID: {message.chat.id}")
                    await Mbot.send_message(LOG_GROUP, traceback.format_exc())

    except Exception as e:
        print(f"Unexpected Error: {e}")
        if LOG_GROUP:
            await Mbot.send_message(LOG_GROUP, f"Unexpected Error: {e}\nChat ID: {message.chat.id}")
            await Mbot.send_message(LOG_GROUP, traceback.format_exc())

    finally:
        # Store media in dump group
        if DUMP_GROUP and "dump_file" in locals():
            await dump_file.copy(DUMP_GROUP)

        await processing_msg.delete()
        await message.reply("Check out @spotifyXMusicBot 🎵 and @DeadlineTech 📢\nSupport us with /donate to maintain this project!")
