
import discord
from dotenv import load_dotenv
import io
import json
import os
import requests


class Plex:

    def __init__(self):
        self.webhook = None
        self._get_webhook()

    def handle_event(self, payload):
        data = json.loads(payload['payload'])
        event = data['event']

        if event != 'library.new':
            return

        metadata = data['Metadata']
        self._send_webhook(metadata)

    def _send_webhook(self, metadata):
        thumbnail = self._download_thumbnail(metadata['thumb'])
        embed = discord.Embed()
        embed.title = f'{metadata["title"]}'
        embed.description = metadata["summary"]
        embed.add_field(name = 'Year', value = metadata['year'])

        if thumbnail:
            embed.set_thumbnail(url = 'attachment://cover.jpg')

        self.webhook.send(embed = embed, file = thumbnail)

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

    def _get_webhook(self):
        webhook_url = os.environ.get('DISCORD_WEBHOOK')
        r = requests.get(webhook_url).json()
        webhook_id = r['id']
        webhook_token = r['token']

        self.webhook = discord.Webhook.partial(webhook_id, webhook_token, adapter = discord.RequestsWebhookAdapter())
