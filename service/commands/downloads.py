import discord
from discord import app_commands
import json
import redis

from utilities.helpers import build_embed


class DownloadCommands(app_commands.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'dl'
        self.db = redis.Redis(host='redis', port=6379, decode_responses=True)

    @app_commands.command(description = 'Add a download to the list to be downloaded')
    async def request(self, ctx, request: str):
        current_list = []

        if self.db.exists('download_list'):
            current_list = json.loads(self.db.get('download_list'))

        current_list.append(request)
        self.db.set('download_list', json.dumps(current_list))

        await ctx.response.send_message(content = f'Added your request of ***{request}*** to the list')

    @app_commands.command(description = 'What is currently on the list to be downloaded')
    async def show(self, ctx):
        current_list = []

        if self.db.exists('download_list'):
            current_list = json.loads(self.db.get('download_list'))

        embed = discord.Embed(title = f'Download Request List', type = 'rich')
        embed.description = '\n'.join(current_list)
        await ctx.response.send_message(embed = embed)

    @app_commands.command(description = 'Remove item from list')
    async def remove(self, ctx, item: str):
        current_list = []

        if not self.db.exists('download_list'):
            await ctx.response.send_message(content = 'There is nothing to remove')
            return

        current_list = json.loads(self.db.get('download_list'))

        if item not in current_list:
            await ctx.response.send_message(content = f'***{item}*** is not in the list, please try again')

        current_list.remove(item)
        self.db.set('download_list', json.dumps(current_list))

        await ctx.response.send_message(content = f'***{item}*** removed from the list')

