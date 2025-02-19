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
        
        # Convert Twitter/X links to fxtwitter.com for direct media download
        if "x.com" in link:
            link = link.replace("x.com", "fxtwitter.com")
        elif "twitter.com" in link:
            link = link.replace("twitter.com", "fxtwitter.com")

        m = await message.reply_sticker("CAACAgIAAxkBATWhF2Qz1Y-FKIKqlw88oYgN8N82FtC8AAJnAAPb234AAT3fFO9hR5GfHgQ")

        # Try sending video directly
        try:
            dump_file = await message.reply_video(link, caption="Thank you for using - @DeadlineReelbot")
        except Exception as e:
            print(f"Error: {e}")
            
            # Retry after sending a temporary text message
            try:
                snd_message = await message.reply("Fetching media, please wait...")
                await asyncio.sleep(1)
                dump_file = await message.reply_video(link, caption="Thank you for using - @DeadlineReelbot")
                await snd_message.delete()
            except Exception as e:
                print(f"Retry failed: {e}")
                await snd_message.delete()

                # Fetch page content manually
                try:
                    response = requests.get(link)
                    if response.status_code != 200:
                        raise Exception(f"Failed to fetch page, status code: {response.status_code}")

                    soup = bs4.BeautifulSoup(response.text, "html.parser")
                    
                    # Find video or image meta tag
                    meta_tag = soup.find("meta", attrs={"property": "og:video"}) or \
                               soup.find("meta", attrs={"property": "og:image"})

                    if meta_tag:
                        content_value = meta_tag.get("content", "")

                        if content_value:
                            try:
                                dump_file = await message.reply_video(
                                    content_value, caption="Thank you for using - @DeadlineReelbot"
                                )
                            except Exception as e:
                                print(f"Error sending video: {e}")
                                snd_msg = await message.reply(content_value)
                                await asyncio.sleep(1)
                                await snd_msg.delete()
                        else:
                            raise Exception("No valid media content found in metadata.")
                    else:
                        raise Exception("No media metadata found.")

                except Exception as e:
                    print(f"Final Error: {e}")
                    await message.reply("❌ **Error:** Invalid link or media is not available.")
                    if LOG_GROUP:
                        await Mbot.send_message(LOG_GROUP, f"Twitter Fetch Error: {e}\n{message.chat.id}")
                        await Mbot.send_message(LOG_GROUP, traceback.format_exc())

    except Exception as e:
        print(f"Unexpected Error: {e}")
        if LOG_GROUP:
            await Mbot.send_message(LOG_GROUP, f"Unexpected Error: {e}\n{message.chat.id}")
            await Mbot.send_message(LOG_GROUP, traceback.format_exc())

    finally:
        if DUMP_GROUP and "dump_file" in locals():
            await dump_file.copy(DUMP_GROUP)
        await m.delete()
        await message.reply("Check out @spotifyXMusicBot 🎵 and @DeadlineTech 📢\nSupport us with /donate to maintain this project!")
