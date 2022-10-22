import asyncio
import os
import re

from telethon.tl.types import InputWebDocument
import aiohttp
import yaml

import generic_bot

# TODO: search for artists and playlists


def env_constructor(loader, node):
    return os.environ.get(loader.construct_scalar(node), None)


yaml.SafeLoader.add_constructor("!env", env_constructor)

if __name__ == '__main__':
    with open("config.yml", 'r') as f:
        config = yaml.safe_load(f)

    async def start():
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }

        async with aiohttp.ClientSession(headers=headers) as http_sess:
            async with http_sess.get("https://listen.tidal.com/") as resp:
                data = await resp.text()

            async with http_sess.get(f"https://listen.tidal.com" + re.search(r'<script (?:defer=\"defer\" )?src=\"(/app\..+?\.js)\"(?: defer=\"defer\")?>', data)[1]) as resp:
                data = await resp.text()

            token = re.search(r":\"(.{16})\":[a-zA-Z]+\(\)\?", data)[1]

            # types=ARTISTS,ALBUMS,TRACKS,VIDEOS,PLAYLISTS

            async def track(query, builder, limit=10, country_code=config['tidal_settings']['country_code']):
                async with http_sess.get("https://listen.tidal.com/v1/search", params={
                    "types": "TRACKS", "includeContributors": "true", "countryCode": country_code, "limit": limit, "query": query
                }, headers={
                    "x-tidal-token": token
                }) as resp:
                    return [
                        await builder.article(
                            title=el['title'] if 'version' not in el or not el['version'] else f"{el['title']} ({el['version']})",
                            text=el['url'],
                            description=f"Artist: {el['artists'][0]['name']}\nAlbum: {el['album']['title']}",
                            thumb=InputWebDocument(
                                url=f"https://resources.tidal.com/images/{el['album']['cover'].replace('-', '/')}/320x320.jpg",
                                size=0, mime_type="image/jpeg", attributes=[],
                            ) if el['album']['cover'] is not None else None
                        ) for el in (await resp.json())['tracks']['items']
                    ]

            async def album(query, builder, limit=10, country_code=config['tidal_settings']['country_code']):
                async with http_sess.get("https://listen.tidal.com/v1/search", params={
                    "types": "ALBUMS", "includeContributors": "true", "countryCode": country_code, "limit": limit, "query": query
                }, headers={
                    "x-tidal-token": token
                }) as resp:
                    return [
                        await builder.article(
                            title=el['title'], text=el['url'],
                            description=f"Artist: {el['artists'][0]['name']}\nTracks: {el['numberOfTracks']}",
                            thumb=InputWebDocument(
                                url=f"https://resources.tidal.com/images/{el['cover'].replace('-', '/')}/320x320.jpg",
                                size=0, mime_type="image/jpeg", attributes=[],
                            ) if el['cover'] is not None else None
                        ) for el in (await resp.json())['albums']['items']
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
