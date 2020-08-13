import asyncio
import logging

import aiohttp
import yaml
from telethon.tl.types import InputWebDocument
from telethon import TelegramClient, events

# TODO: non-inline command
# TODO: search for artists, playlists and radios


class Namespace(dict):
    def __getattr__(self, *args, **kwargs):
        return self.__getitem__(*args, **kwargs)


async def main():
    with open("config.yml", 'r') as f:
        config = Namespace(yaml.safe_load(f))

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=config.log_level)
    # logger = logging.getLogger(__name__)

    client = TelegramClient(**config.telethon_settings)
    print("Starting")
    await client.start(bot_token=config.bot_token)
    print("Started")

    async with aiohttp.ClientSession() as http_sess:
        @client.on(events.InlineQuery)
        async def inline_handler(event):
            builder = event.builder

            if not event.text or len(event.text) < 2:
                await event.answer()
                return

            if not event.text.startswith("."):
                mode = ".track"
                query = event.text
            elif " " in event.text:
                mode, query = event.text.split(maxsplit=1)
            else:
                await event.answer()
                return

            async def track():
                async with http_sess.get("https://api.deezer.com/search/track", params={"limit": 10, "q": query}) as resp:
                    await event.answer([
                        builder.article(
                            title=el['title'],
                            text=el['link'],
                            description=f"Artist: {el['artist']['name']}\nAlbum: {el['album']['title']}",
                            thumb=InputWebDocument(
                                url=el['album']['cover_medium'],
                                size=0,
                                mime_type="image/jpeg",
                                attributes=[],
                            ),
                        ) for el in (await resp.json())['data'] if el['type'] == "track"])

            async def album():
                async with http_sess.get("https://api.deezer.com/search/album", params={"limit": 10, "q": query}) as resp:
                    await event.answer([
                        builder.article(
                            title=el['title'],
                            text=el['link'],
                            description=f"Artist: {el['artist']['name']}\nTracks: {el['nb_tracks']}",
                            thumb=InputWebDocument(
                                url=el['cover_medium'],
                                size=0,
                                mime_type="image/jpeg",
                                attributes=[],
                            ),
                        ) for el in (await resp.json())['data'] if el['type'] == "album"])

            modes = {
                ".t": track,
                ".track": track,
                ".a": album,
                ".album": album
            }

            if mode not in modes:
                await event.answer([builder.article("Bad mode", description="Usage: .track/.t/.album/.a + title or just title for track",
                                                    text="Invalid search type, please try again.")])
            else:
                await modes[mode]()

        async with client:
            print("Good morning!")
            await client.run_until_disconnected()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
