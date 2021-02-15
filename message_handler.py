
from dotenv import load_dotenv
import os
import requests


class MessageHandler:
    load_dotenv()
    domain = 'https://discord.com/api/v8/applications'
    application_id = os.environ.get('APPLICATION_ID')
    guild_id = os.environ.get('GUILD_ID')
    token = os.environ.get('BOT_TOKEN')
    headers = {'Authorization': f'Bot {token}'}
    url = f'{domain}/{application_id}/guilds/{guild_id}/commands'

    def list_commands(self):
        commands = requests.get(self.url, headers = self.headers).json()
        data = []

        for command in commands:
            data.append(f"{command['name']}: {command['id']}")

        return '\n'.join(data)

    def remove_command(self, id):
        url = f'{self.url}/{id}'
        requests.delete(url, headers = self.headers)
        return f'Removed command {id}'
