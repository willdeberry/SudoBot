
from dotenv import load_dotenv
import os
import requests

from logger import logger


class DiscordCommands:
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
            data.append({'name': command['name'], 'value': command['description']})

        return data

    def remove_command(self, id):
        url = f'{self.url}/{id}'
        requests.delete(url, headers = self.headers)
        return f'Removed command {id}'

    def register_commands(self):
        logger.info('Register commands')
        commands = [
            {
                "name": "fyc",
                "description": "Fuck your couch",
                "type": 1
            },
            {
                "name": "tbl",
                "description": "TBL Information",
                "options": [
                    {
                        "name": "next",
                        "description": "When is the next game",
                        "type": 1
                    },
                    {
                        "name": "record",
                        "description": "What is the TBL's current record",
                        "type": 1
                    }
                ]
            },
            {
                "name": "stocks",
                "description": "Stock information",
                "options": [
                    {
                        "name": "price",
                        "description": "Price of the stock",
                        "type": 3
                    }
                ]
            }
        ]

        for command in commands:
            logger.info('Registering command {}', command)
            requests.post(self.url, headers = self.headers, json = command)
