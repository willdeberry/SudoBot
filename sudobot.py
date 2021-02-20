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

token = os.environ.get('BOT_TOKEN')
sports_channel_id = os.environ.get('SPORTS_CHANNEL')
guild_id = os.environ.get('GUILD_ID')


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


def find_emoji(emojis, name):
    for emoji in emojis:
        if emoji.name == name.lower():
            return emoji


def build_embed(title, fields):
    embed = discord.Embed(title = title, type = 'rich')

    for field in fields:
        embed.add_field(name = field['name'], value = field['value'])

    return embed


async def report_score(score):
    home_name = score['home']['name']
    home_score = score['home']['score']
    away_name = score['away']['name']
    away_score = score['away']['score']
    _sports_channel = client.fetch_channel(sports_channel_id)
    sports_channel = await _sports_channel
    guild = client.get_guild(int(guild_id))
    emojis = guild.emojis
    goal_emoji = find_emoji(emojis, 'goal')
    home_team_emoji = find_emoji(emojis, home_name)
    away_team_emoji = find_emoji(emojis, away_name)
    fields = [{'name': f'{name}  {name}  {name}', 'value': f'{home_score} - {away_score}'}]
    embed = build_embed('Goal Scored', fields)

    await sports_channel.send(embed = embed)


@tasks.loop(seconds = 5)
async def check_score():
    score = hockey_game.did_score()

    if score['update']:
        await report_score(score)


def start_bot():
    logger.info('Logging in with bot')
    client.run(token)


def main():
    discord_commands.register_commands()
    start_bot()


if __name__ == '__main__':
    main()
