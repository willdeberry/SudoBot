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
    read_only_channels = ['downloads', 'plex', 'server-status']
    sports_channel = None
    game_status = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.discord_commands.register_commands()

    async def on_ready(self):
        logger.info(f'Bot logged in as {self.user}')
        await self.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = 'for $udo'))
        self.check_score.start()

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

    @tasks.loop(seconds = 5)
    async def check_score(self):
        self.sports_channel = await self.fetch_channel(os.environ.get('SPORTS_CHANNEL'))

        game = self.hockey_game.did_score()

        if game['scheduled'] and game['scheduled'] != self.game_status.get('scheduled'):
            await self._report_game_scheduled()

        if game['start'] and game['start'] != self.game_status.get('start'):
            await self._report_game_start()

        if game['goal']:
            await self._report_score()

        if not self.game_status:
            self.game_status = game

    @check_score.before_loop
    async def before_check_score(self):
        logger.info('waiting for bot to start loop...')
        await self.wait_until_ready()

    async def handle_readonly(self, message):
        allowed_posters = ['Plex#0000', 'transmission#0000', 'UptimeRobot#0000']

        if str(message.author) in allowed_posters:
            return

        logger.info(f'removing message from read only room posted by {message.author}')
        await message.delete()

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
        score = self.hockey_game.format_score()
        home = score['home']
        away = score['away']
        content = f"Goal Scored: {home['name']} {home['score']} - {away['name']} {away['score']}"

        await self.sports_channel.send(content = content)

    async def _report_game_scheduled(self):
        data = self.hockey_game.get_game_data()
        home_name = data['home']['name']
        home_record = data['home']['record']
        away_name = data['away']['name']
        away_record = data['away']['record']
        tv_channels = ', '.join(data['broadcasts'])
        goal_emoji = self._find_emoji_in_guild('goal')

        fields = [
                {'name': 'Date', 'value': f"{data['time']} @ {data['venue']}"},
                {'name': 'Matchup', 'value': f"{away_name} ({away_record}) vs {home_name} ({home_record})"},
                {'name': 'Broadcasts', 'value': tv_channels, 'inline': True},
                {'name': 'Streams', 'value': '[CastStreams](https://www.caststreams.com/), [CrackStreams](http://crackstreams.biz/nhlstreams/)', 'inline': True}
            ]

        embed = self._build_embed(f'{goal_emoji} Today is Gameday! {goal_emoji}', fields, inline = False)

        await self.sports_channel.send(embed = embed)

    async def _report_game_start(self):
        tbl_emoji = self._find_emoji_in_guild('tbl')

        fields = [{'name': f'{tbl_emoji}', 'value': 'Time to tune in!'}]
        embed = self._build_embed('Game Start', fields, inline = False)

        await self.sports_channel.send(embed = embed)


def main():
    intents = discord.Intents.default()
    intents.message_content = True
    client = SudoBot(intents = intents)
    client.run(os.environ.get('BOT_TOKEN'))


if __name__ == '__main__':
    main()
