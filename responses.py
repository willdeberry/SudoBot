import requests

from commands import DiscordCommands
from hockey import Hockey


class CommandResponse:
    commands = DiscordCommands()
    hockey = Hockey()

    def __init__(self, response):
        self.command_payload = response['data']
        self.command_name = self.command_payload['name']
        self.options = self.command_payload.get('options', None)

    def list_commands(self):
        return self.commands.list_commands()

    def remove_command(self, options):
        command_options = options[0].get('options', None)

        if not command_options:
            return 'Please provide a valid Id to remove.'

        command_to_remove = command_options[0]['value']
        self.commands.remove_command(command_to_remove)
        return f'Removed command {command_to_remove}'

    def parse_response(self):
        if self.command_name == 'fyc':
            return {
                "type": 3,
                "data": {
                    "tts": False,
                    "content": "https://tenor.com/view/rick-james-fuck-yo-couch-dirty-shoes-couch-stomp-gif-16208682",
                    "embeds": [],
                    "allowed_mentions": []
                }
            }

        if self.command_name == 'tbl':
            if self.options[0]['name'] == 'next':
                return {
                    "type": 3,
                    "data": {
                        "tts": False,
                        "content": "",
                        "embeds": [
                            {
                                "title": "Next TBL Game",
                                "type": "rich",
                                "fields": [
                                    {
                                        "name": "Date",
                                        "value": self.hockey.tbl_next_game()
                                    }
                                ]
                            }
                        ],
                        "allowed_mentions": []
                    }
                }

            if self.options[0]['name'] == 'record':
                data = self.hockey.tbl_record()
                return {
                    "type": 3,
                    "data": {
                        "tts": False,
                        "content": "",
                        "embeds": [
                            {
                                "title": "TBL Current Record",
                                "type": "rich",
                                "fields": [
                                    {
                                        "name": "Games Played",
                                        "value": data['games_played']
                                    },
                                    {
                                        "name": "Wins",
                                        "value": data['wins']
                                    },
                                    {
                                        "name": "Losses",
                                        "value": data['losses']
                                    },
                                    {
                                        "name": "OT",
                                        "value": data['ot']
                                    },
                                    {
                                        "name": "Points",
                                        "value": data['points']
                                    }
                                ]
                            }
                        ],
                        "allowed_mentions": []
                    }
                }
