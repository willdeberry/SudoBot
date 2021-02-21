
import requests

from hockey import Hockey
from stocks import Stocks


class CommandResponse:
    hockey = Hockey()
    stocks = Stocks()

    def __init__(self, response):
        self.command_payload = response['data']
        self.command_name = self.command_payload['name']
        self.options = self.command_payload.get('options', None)

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
                return self.hockey.tbl_next_game()

            if self.options[0]['name'] == 'record':
                return self.hockey.tbl_record()

            if self.options[0]['name'] == 'score':
                return self.hockey.tbl_score()

        if self.command_name == 'stocks':
            if self.options[0]['name'] == 'price':
                ticker = self.options[0]['value']
                return self.stocks.get_price(ticker)
