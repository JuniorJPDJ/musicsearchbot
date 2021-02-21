import asyncio
import re

from telethon.tl.types import InputWebDocument
import aiohttp
import yaml

import generic_bot

# TODO: search for artists and playlists


if __name__ == '__main__':
    with open("config.yml", 'r') as f:
        config = yaml.safe_load(f)

    async def start():
        async with aiohttp.ClientSession() as http_sess:
            async with http_sess.get("https://listen.tidal.com/") as resp:
                data = await resp.text()

            async with http_sess.get(f"https://listen.tidal.com" + re.search(r'<script src=\"(/app.+?)\">', data)[1]) as resp:
                data = await resp.text()

            token = re.search(r"const a=.+?.\.config\.enableDesktopFeatures\?\".+?\"\:\"(.{16})\"", data)[1]

            # types=ARTISTS,ALBUMS,TRACKS,VIDEOS,PLAYLISTS

            async def track(query, builder, limit=10, country_code=config['tidal_settings']['country_code']):
                async with http_sess.get("https://listen.tidal.com/v1/search", params={
                    "types": "TRACKS", "includeContributors": "true", "countryCode": country_code, "limit": limit, "query": query
                }, headers={
                    "x-tidal-token": token
                }) as resp:
                    return [
                        await builder.article(
                            title=el['title'], text=el['url'],
                            description=f"Artist: {el['artists'][0]['name']}\nAlbum: {el['album']['title']}",
                            thumb=InputWebDocument(
                                url=f"https://resources.tidal.com/images/{el['album']['cover'].replace('-', '/')}/320x320.jpg",
                                size=0, mime_type="image/jpeg", attributes=[],
                            )
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
                            )
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

    asyncio.get_event_loop().run_until_complete(start())
