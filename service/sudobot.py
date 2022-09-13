#!/usr/bin/env python3

import asyncio
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import os

from nhl import HockeyGame
from logger import logger
from message_handler import DiscordCommands
from status import Status


load_dotenv()


class SudoBot(discord.Client):
    discord_commands = DiscordCommands()
    hockey_game = HockeyGame()
    status = Status(os.environ.get('UPTIME_ROBOT_API_KEY'))
    read_only_channels = ['downloads', 'server-status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.discord_commands.register_commands()

        self.bg_task = self.loop.create_task(self.check_score())

    async def on_ready(self):
        logger.info(f'Bot logged in as {self.user}')
        await self.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = 'for $udo'))

    async def on_message(self, message):
        logger.info(f'Received message in {message.channel.name} from {message.author}: {message.content}')
        if message.author == self.user:
            return

        if message.channel.name in self.read_only_channels:
            await self.handle_readonly(message)

        if message.content.startswith('$udo'):
            subcommand = message.content.split(' ')[1]

            if subcommand == 'list':
                slash_commands = self.discord_commands.list_commands()
                slash_command_embed = self._build_embed('Slash Commands', slash_commands, inline = False)
                await message.channel.send(embed = slash_command_embed)

                commands = [
                    {'name': 'list', 'value': 'Shows a list of commands available'},
                    {'name': 'remove', 'value': 'Remove a slash command'},
                    {'name': 'status', 'value': 'Current health of the servers and bot'}
                ]
                command_embed = self._build_embed('$udo Commands', commands, inline = False)
                await message.channel.send(embed = command_embed)

            if subcommand == 'remove':
                if message.author.name != 'Will':
                    await message.channel.send('You are not authorized to run this command')
                    return

                try:
                    command_id = message.content.split(' ')[2]
                    response = self.discord_commands.remove_command(command_id)
                except IndexError:
                    response = 'Please provide id of the command to remove'

                await message.channel.send(response)

            if subcommand == 'status':
                current_status = self.status.get_current()
                embed = self._build_embed('Current server statuses', current_status)
                await message.channel.send(embed = embed)


        if 'weed' in message.content.lower():
            weed_emoji = discord.utils.get(message.guild.emojis, name='weed')
            await message.add_reaction(weed_emoji)

        if 'jeep' in message.content.lower():
            jeep_emoji = discord.utils.get(message.guild.emojis, name='rubberduck')
            await message.add_reaction(jeep_emoji)

    def _find_emoji_in_guild(self, name):
        guild = self.get_guild(int(os.environ.get('GUILD_ID')))
        emojis = guild.emojis

        for emoji in emojis:
            if emoji.name == name.lower():
                return emoji

    def _build_embed(self, title, fields, inline = True):
        embed = discord.Embed(title = title, type = 'rich')

        for field in fields:
            embed.add_field(name = field['name'], value = field['value'], inline = inline)

        return embed


    async def _report_score(self):
        _sports_channel = self.fetch_channel(os.environ.get('SPORTS_CHANNEL'))
        sports_channel = await _sports_channel
        goal_emoji = self._find_emoji_in_guild('goal')

        fields = [{'name': f'{goal_emoji}  {goal_emoji}  {goal_emoji}', 'value': self.hockey_game.format_score()}]
        embed = self._build_embed('Goal Scored', fields, inline = False)

        await sports_channel.send(embed = embed)

    async def _report_game_start(self):
        _sports_channel = self.fetch_channel(os.environ.get('SPORTS_CHANNEL'))
        sports_channel = await _sports_channel
        tbl_emoji = self._find_emoji_in_guild('tbl')

        fields = [{'name': f'{tbl_emoji}', 'value': 'Time to tune in!'}]
        embed = self._build_embed('Game Start', fields, inline = False)

        await sports_channel.send(embed = embed)

    async def check_score(self):
        await self.wait_until_ready()
        logger.info('checking score')

        while not self.is_closed():
            game = self.hockey_game.did_score()

            if game['start']:
                logger.info('game start')
                await self._report_game_start()

            if game['goal']:
                await self._report_score()

            await asyncio.sleep(5)

    async def handle_readonly(self, message):
        allowed_posters = ['transmission#0000', 'UptimeRobot#0000']

        logger.info(f'removing message from read only room posted by {message.author}')

        if message.author in allowed_posters:
            return

        await message.delete()


def main():
    intents = discord.Intents.default()
    intents.message_content = True
    client = SudoBot(intents = intents)
    client.run(os.environ.get('BOT_TOKEN'))


if __name__ == '__main__':
    main()
