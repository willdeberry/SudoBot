import requests
import os

from dotenv import load_dotenv
load_dotenv()


class DiscordCommands:
    domain = 'https://discord.com/api/v8/applications'
    application_id = os.environ.get('APPLICATION_ID')
    guild_id = os.environ.get('GUILD_ID')
    token = os.environ.get('BOT_TOKEN')
    headers = {'Authorization': f'Bot {token}'}
    url = f'{domain}/{application_id}/guilds/{guild_id}/commands'

    def register_commands(self):
        commands1 = {
            "name": "commands",
            "description": "Manage your server commands via a command",
            "options": [
                {
                    "name": "list",
                    "description": "List registered commands",
                    "type": 1
                },
                {
                    "name": "remove",
                    "description": "Remove specific command",
                    "type": 1,
                    "options": [
                        {
                            "name": "id",
                            "description": "Id of the command to remove",
                            "type": 3
                        }
                    ]
                }
            ]
        }
        requests.post(self.url, headers = self.headers, json = commands1)

        commands2 = {
            "name": "fyc",
            "description": "Fuck your couch",
            "type": 1
        }
        requests.post(self.url, headers = self.headers, json = commands2)

        commands3 = {
            "name": "tbl",
            "description": "What's the next TBL game",
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
        }
        requests.post(self.url, headers = self.headers, json = commands3)

    def list_commands(self):
        commands = requests.get(self.url, headers = self.headers).json()
        data = []

        for command in commands:
            data.append(f"{command['name']}: {command['id']}")

        return '\n'.join(data)

    def remove_command(self, id):
        url = f'{self.url}/{id}'
        requests.delete(url, headers = self.headers)
        return True
