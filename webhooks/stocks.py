
from dotenv import load_dotenv
import os
import requests


class Stocks:

    def get_price(self, ticker):
        load_dotenv()
        token = os.environ.get('STOCK_TOKEN')
        response = requests.get(f'http://api.marketstack.com/v1/eod/latest?access_key={token}&symbols={ticker}').json()

        try:
            name = ticker.upper()
            price = response['data'][0]['close']
        except KeyError:
            name = 'Error'
            price = response['error']['message']

        return {
            "type": 4,
            "data": {
                "tts": False,
                "content": "",
                "embeds": [
                    {
                        "title": f'{name}',
                        "type": "rich",
                        "fields": [
                            {
                                "name": "Price",
                                "value": f'{price}'
                            }
                        ]
                    }
                ],
                "allowed_mentions": []
            }
        }
