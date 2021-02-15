
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

    def register_commands(self):
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
            requests.post(self.url, headers = self.headers, json = command)
