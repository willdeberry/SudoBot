
import requests
import os

from dotenv import load_dotenv


class DiscordCommands:
    load_dotenv()
    domain = 'https://discord.com/api/v8/applications'
    application_id = os.environ.get('APPLICATION_ID')
    guild_id = os.environ.get('GUILD_ID')
    token = os.environ.get('BOT_TOKEN')
    headers = {'Authorization': f'Bot {token}'}
    url = f'{domain}/{application_id}/guilds/{guild_id}/commands'
