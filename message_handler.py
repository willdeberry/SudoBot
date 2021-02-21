
from dotenv import load_dotenv
import os
import requests

from logger import logger


class DiscordCommands:
    load_dotenv()
    _domain = 'https://discord.com/api/v8/applications'
    _application_id = os.environ.get('APPLICATION_ID')
    _guild_id = os.environ.get('GUILD_ID')
    _token = os.environ.get('BOT_TOKEN')
    _headers = {'Authorization': f'Bot {_token}'}
    _url = f'{_domain}/{_application_id}/guilds/{_guild_id}/commands'

    def list_commands(self):
        commands = requests.get(self._url, headers = self._headers).json()
        data = []

        for command in commands:
            data.append({'name': command['name'], 'value': command['description']})

        return data

    def remove_command(self, id):
        url = f'{self._url}/{id}'
        requests.delete(url, headers = self._headers)
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
                    },
                    {
                        "name": "score",
                        "description": "What is the score of the in progress game",
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
            requests.post(self._url, headers = self._headers, json = command)
