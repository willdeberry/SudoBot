
import asyncio
import json
import requests

from utilities.helpers import build_embed
from utilities.logger import logger


class Ollama:
    async def ask(self, message):
        url = 'http://direct.sudoservers.com:11434/api/generate'
        params = {'Content-Type': 'application/json'}
        data = { 'model': 'llama2-uncensored', 'prompt': message, 'stream': False }
        result = await asyncio.to_thread(requests.post, url, params = params, json = data)
        response = result.json()

        logger.info(f'content: {response["response"]}')

        return response['response']
