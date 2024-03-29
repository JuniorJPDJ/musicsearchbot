import asyncio
import os

from telethon.tl.types import InputWebDocument
import aiohttp
import yaml

import generic_bot

# TODO: search for artists, playlists and radios


def env_constructor(loader, node):
    return os.environ.get(loader.construct_scalar(node), None)


yaml.SafeLoader.add_constructor("!env", env_constructor)

if __name__ == '__main__':
    with open("config.yml", 'r') as f:
        config = yaml.safe_load(f)

    async def start():
        async with aiohttp.ClientSession() as http_sess:

            async def track(query, builder, limit=10):
                async with http_sess.get("https://api.deezer.com/search/track", params={"limit": limit, "q": query}) as resp:
                    return [
                        await builder.article(
                            title=el['title'], text=el['link'],
                            description=f"Artist: {el['artist']['name']}\nAlbum: {el['album']['title']}",
                            thumb=InputWebDocument(
                                url=el['album']['cover_medium'], size=0, mime_type="image/jpeg", attributes=[],
                            ) if el['album']['cover_medium'] is not None else None
                        ) for el in (await resp.json())['data'] if el['type'] == "track"
                    ]

            async def album(query, builder, limit=10):
                async with http_sess.get("https://api.deezer.com/search/album", params={"limit": limit, "q": query}) as resp:
                    return [
                        await builder.article(
                            title=el['title'], text=el['link'],
                            description=f"Artist: {el['artist']['name']}\nTracks: {el['nb_tracks']}",
                            thumb=InputWebDocument(
                                url=el['cover_medium'], size=0, mime_type="image/jpeg", attributes=[],
                            ) if el['cover_medium'] is not None else None
                        ) for el in (await resp.json())['data'] if el['type'] == "album"
                    ]

            modes = {
                None: track,
                ".t": track,
                ".track": track,
                ".a": album,
                ".album": album
            }

            await generic_bot.main(config, modes)

    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(start())
