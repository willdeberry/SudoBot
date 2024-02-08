#!/usr/bin/env python3

import discord
from dotenv import load_dotenv
import os
from socket import gethostbyname

from utilities.helpers import build_embed
from utilities.logger import logger
from commands.ollama import Ollama
from commands.status import Status
from commands.tbl import TBLCommands
from sports.updates import HockeyUpdates


load_dotenv()


class SudoBot(discord.Client):
    guild_id = discord.Object(id = os.environ['GUILD_ID'])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild = self.guild_id)
        await self.tree.sync(guild = self.guild_id)

    async def on_ready(self):
        logger.info(f'Bot logged in as {self.user}')
        general_channel = await self.fetch_channel(os.environ.get('GENERAL_CHANNEL'))
        sports_channel = await self.fetch_channel(os.environ.get('SPORTS_CHANNEL'))
        guild = self.get_guild(int(os.environ.get('GUILD_ID')))
        hockey_updates = HockeyUpdates(guild, general_channel, sports_channel)
        hockey_updates.check_score.start()

    async def on_message(self, message):
        try:
            logger.info(f'Received message in {message.channel.name} from {message.author}: {message.content}')
        except:
            pass

        read_only_channels = ['downloads', 'plex', 'server-status']

        if message.author == self.user:
            return

        if message.channel.name in read_only_channels:
            await self._handle_readonly(message)

        if 'weed' in message.content.lower():
            weed_emoji = discord.utils.get(message.guild.emojis, name='weed')
            await message.add_reaction(weed_emoji)

        if 'jeep' in message.content.lower():
            jeep_emoji = discord.utils.get(message.guild.emojis, name='rubberduck')
            await message.add_reaction(jeep_emoji)

    async def _handle_readonly(self, message):
        allowed_posters = ['Plex#0000', 'transmission#0000', 'UptimeRobot#0000']

        if str(message.author) in allowed_posters:
            return

        logger.info(f'removing message from read only room posted by {message.author}')
        await message.delete()


def main():
    intents = discord.Intents.default()
    intents.message_content = True
    client = SudoBot(intents = intents)

    @client.tree.command(description = 'Fuck your couch mofo')
    async def fyc(ctx):
        await ctx.response.send_message(content = 'https://tenor.com/view/rick-james-fuck-yo-couch-dirty-shoes-couch-stomp-gif-16208682')

    @client.tree.command(description = 'Gang gang')
    async def gang(ctx):
        await ctx.response.send_message(content = 'https://sudobot-images.s3.amazonaws.com/gang.png')

    @client.tree.command(description = 'Our lord and savior...heeeyyyy!')
    async def savior(ctx):
        await ctx.response.send_message(content = 'https://tenor.com/view/buddy-christ-dogma-george-carlin-thumbs-up-gif-3486405')

    @client.tree.command(description = 'IP address of the dedicated game server')
    async def server(ctx):
        ip = gethostbyname('direct.sudoservers.com')
        await ctx.response.send_message(content = ip)

    @client.tree.command(description = 'Display current server status')
    async def status(ctx):
        status = Status(os.environ.get('UPTIME_ROBOT_API_KEY'))
        current_status = status.get_current()
        embed = build_embed('Current server statuses', current_status)
        await ctx.response.send_message(embed = embed)

    @client.tree.command(description = 'Ask the bot a question')
    async def ask(ctx, question: str):
        await ctx.response.defer()
        ollama = Ollama()
        response = await ollama.ask(question)
        embed = discord.Embed(title = f'Question: {question}', type = 'rich')
        embed.description = response
        await ctx.followup.send(embed = embed)

    client.tree.add_command(TBLCommands(), guild = client.guild_id)
    client.run(os.environ.get('BOT_TOKEN'))


if __name__ == '__main__':
    main()
