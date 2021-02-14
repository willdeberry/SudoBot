
import discord
from dotenv import load_dotenv
import os


load_dotenv()


class Bot:
    token = os.environ.get('BOT_TOKEN')
    client = discord.Client()
    client.run(token)

    @client.event
    async def on_ready():
        print(f'Bot logged in as {client.user}')
