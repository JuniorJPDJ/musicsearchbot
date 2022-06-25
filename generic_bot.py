import logging

from telethon import TelegramClient, events
from telethon.tl.custom import InlineBuilder

# TODO: non-inline command


async def main(config, modes):
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=config['log_level'])
    # logger = logging.getLogger(__name__)

    client = TelegramClient(**config['telethon_settings'])
    print("Starting")
    await client.start(bot_token=config['bot_token'])
    print("Started")

    builder = InlineBuilder(client)

    @client.on(events.InlineQuery)
    async def inline_handler(event):
        if not event.text or len(event.text) < 2:
            await event.answer([builder.article("Help message", description="Usage: .track/.t/.album/.a + title or just title for track",
                                                text="Help message.")])
            return

        if not event.text.startswith("."):
            mode = None
            query = event.text
        elif " " in event.text:
            mode, query = event.text.split(maxsplit=1)
        else:
            await event.answer()
            return

        if mode not in modes:
            await event.answer([builder.article("Bad mode", description="Usage: .track/.t/.album/.a + title or just title for track",
                                                text="Invalid search type, please try again.")])
        else:
            await event.answer(
                await modes[mode](query, builder) or
                [builder.article("No search results found", description="Try another query",
                                                text="No search results found.")]
            )

    async with client:
        print("Good morning!")
        await client.run_until_disconnected()
