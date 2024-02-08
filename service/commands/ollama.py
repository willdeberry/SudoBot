
import asyncio
import json
import requests

from utilities.helpers import build_embed
from utilities.logger import logger


class Ollama:
    _url = 'http://direct.sudoservers.com:11434/api/generate'
    _params = {'Content-Type': 'application/json'}

    async def ask(self, message):
        data = { 'model': 'llama2-uncensored', 'prompt': message, 'stream': False }
        result = await asyncio.to_thread(requests.post, self._url, params = self._params, json = data)
        response = result.json()

        return response['response']

    async def code(self, message):
        data = { 'model': 'codellama:13b', 'prompt': message, 'stream': False }
        result = await asyncio.to_thread(requests.post, self._url, params = self._params, json = data)
        response = result.json()

        return response['response']
