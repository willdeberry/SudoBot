
import aiohttp
import datetime
import discord
from dotenv import load_dotenv
import io
import json
import os
import requests


class Plex:

    def __init__(self):
        self.thumbnail = None

    async def handle_event(self, payload):
        data = json.loads(payload['payload'])
        event = data['event']

        if event != 'library.new':
            return

        metadata = data['Metadata']
        embed = self._process_metadata(metadata)
        await self._send_webhook(embed)

    def _process_metadata(self, metadata):
        self.thumbnail = self._download_thumbnail(metadata['thumb'])
        embed = discord.Embed()
        embed.title = f'{metadata["title"]}'
        embed.description = metadata["summary"]

        if metadata['librarySectionType'] == 'show':
            embed.title = f'{metadata["grandparentTitle"]} {metadata["parentTitle"]}: {metadata["title"]}'

        if 'duration' in metadata:
            embed.add_field(name = 'Duration', value = str(datetime.timedelta(0, 0, 0, metadata['duration'])))

        if 'year' in metadata:
            embed.add_field(name = 'Year', value = metadata['year'])

        if self.thumbnail:
            embed.set_thumbnail(url = 'attachment://cover.jpg')

        return embed

    async def _send_webhook(self, embed):
        webhook_url = os.environ.get('DISCORD_WEBHOOK')

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(webhook_url, session = session)
            await webhook.send(embed = embed, file = self.thumbnail)

    def _download_thumbnail(self, thumb):
        url = os.environ.get('PLEX_URL')
        token = os.environ.get('PLEX_TOKEN')
        headers = {'X-Plex-Token': token}

        try:
            thumbnail = requests.get(f'{url}{thumb}', headers = headers)
            thumbnail.raise_for_status()
        except Exception as err:
            return None
        else:
            return discord.File(io.BytesIO(thumbnail.content), 'cover.jpg')
