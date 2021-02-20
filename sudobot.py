#!/usr/bin/env python3

import discord
from discord.ext import tasks
from dotenv import load_dotenv
import os

from game_watcher import HockeyGame
from logger import logger
from message_handler import DiscordCommands
from status import Status


load_dotenv()
client = discord.Client()
discord_commands = DiscordCommands()
hockey_game = HockeyGame()
status = Status(os.environ.get('UPTIME_ROBOT_API_KEY'))


@client.event
async def on_ready():
    logger.info(f'Bot logged in as {client.user}')
    check_score.start()


@client.event
async def on_message(message):
    logger.info(f'Received message in {message.channel.name}: {message.content}')
    if message.author == client.user:
        return

    if message.content.startswith('$sudo'):
        subcommand = message.content.split(' ')[1]

        if subcommand == 'list':
            await message.channel.send(discord_commands.list_commands())

        if subcommand == 'remove':
            if message.author.name != 'Will':
                await message.channel.send('You are not authorized to run this command')
                return

            try:
                command_id = message.content.split(' ')[2]
                response = discord_commands.remove_command(command_id)
            except IndexError:
                response = 'Please provide id of the command to remove'

            await message.channel.send(response)

        if subcommand == 'status':
            current_status = status.get_current()
            embed = build_embed('Current server statuses', current_status)
            await message.channel.send(embed = embed)


    if 'weed' in message.content:
        weed_emoji = discord.utils.get(message.guild.emojis, name='weed')
        await message.add_reaction(weed_emoji)


def find_emoji_in_guild(name):
    guild = client.get_guild(int(os.environ.get('GUILD_ID')))
    emojis = guild.emojis

    for emoji in emojis:
        if emoji.name == name.lower():
            return emoji


def build_embed(title, fields):
    embed = discord.Embed(title = title, type = 'rich')

    for field in fields:
        embed.add_field(name = field['name'], value = field['value'])

    return embed


async def report_score():
    _sports_channel = client.fetch_channel(os.environ.get('SPORTS_CHANNEL'))
    sports_channel = await _sports_channel
    goal_emoji = find_emoji_in_guild('goal')

    fields = [{'name': f'{goal_emoji}  {goal_emoji}  {goal_emoji}', 'value': hockey_game.format_score()}]
    embed = build_embed('Goal Scored', fields)

    await sports_channel.send(embed = embed)


@tasks.loop(seconds = 5)
async def check_score():
    goal = hockey_game.did_score()

    if goal:
        await report_score()


def start_bot():
    logger.info('Logging in with bot')
    client.run(os.environ.get('BOT_TOKEN'))


def main():
    discord_commands.register_commands()
    start_bot()


if __name__ == '__main__':
    main()
