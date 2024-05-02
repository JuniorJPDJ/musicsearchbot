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


async def build_track_entry(builder, el):
    title = (
        el["title"]
        if "version" not in el or not el["version"]
        else f"{el['title']} ({el['version']})"
    )
    artists = ", ".join(map(lambda artist: artist["name"], el["artists"]))
    explicit = el.get("properties", {}).get("content", "") == "explicit"

    artists_label = f"Artists: {artists}" if len(artists) > 1 else f"Artist: {artists}"
    album_label = f"Album: {el['album']['title']}"
    explicit_label = "🔞 " if explicit else ""

    return await builder.article(
        title=f"{explicit_label}{title}",
        text=el["url"],
        description=f"{artists_label}\n{album_label}",
        thumb=(
            InputWebDocument(
                url=f"https://resources.tidal.com/images/{el['album']['cover'].replace('-', '/')}/320x320.jpg",
                size=0,
                mime_type="image/jpeg",
                attributes=[],
            )
            if el["album"]["cover"] is not None
            else None
        ),
    )


async def build_album_entry(builder, el):
    artists = ", ".join(map(lambda artist: artist["name"], el["artists"]))
    explicit = el.get("properties", {}).get("content", "") == "explicit"

    artists_label = f"Artists: {artists}" if len(artists) > 1 else f"Artist: {artists}"
    tracks_label = f"Tracks: {el['numberOfTracks']}"
    explicit_label = "🔞 " if explicit else ""

    return await builder.article(
        title=f"{explicit_label}{el["title"]}",
        text=el["url"],
        description=f"{artists_label}\n{tracks_label}",
        thumb=(
            InputWebDocument(
                url=f"https://resources.tidal.com/images/{el['cover'].replace('-', '/')}/320x320.jpg",
                size=0,
                mime_type="image/jpeg",
                attributes=[],
            )
            if el["cover"] is not None
            else None
        ),
    )


if __name__ == "__main__":
    with open("config.yml", "r") as f:
        config = yaml.safe_load(f)

    async def start():
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        }

        async with aiohttp.ClientSession(headers=headers) as http_sess:
            token = config["tidal_settings"]["token"]

            # types=ARTISTS,ALBUMS,TRACKS,VIDEOS,PLAYLISTS

            async def track(
                query,
                builder,
                limit=10,
                country_code=config["tidal_settings"]["country_code"],
            ):
                async with http_sess.get(
                    "https://listen.tidal.com/v1/search",
                    params={
                        "types": "TRACKS",
                        "includeContributors": "true",
                        "countryCode": country_code,
                        "limit": limit,
                        "query": query,
                    },
                    headers={"x-tidal-token": token},
                ) as resp:
                    return [
                        await build_track_entry(builder, el)
                        for el in (await resp.json())["tracks"]["items"]
                    ]

            async def album(
                query,
                builder,
                limit=10,
                country_code=config["tidal_settings"]["country_code"],
            ):
                async with http_sess.get(
                    "https://listen.tidal.com/v1/search",
                    params={
                        "types": "ALBUMS",
                        "includeContributors": "true",
                        "countryCode": country_code,
                        "limit": limit,
                        "query": query,
                    },
                    headers={"x-tidal-token": token},
                ) as resp:
                    return [
                        build_album_entry(builder, el)
                        for el in (await resp.json())["albums"]["items"]
                    ]

            modes = {
                None: track,
                ".t": track,
                ".track": track,
                ".a": album,
                ".album": album,
            }

            await generic_bot.main(config, modes)

    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(start())
