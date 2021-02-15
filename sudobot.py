#!/usr/bin/env python3

import discord
from dotenv import load_dotenv
import os

from message_handler import MessageHandler


client = discord.Client()
handler = MessageHandler()


@client.event
async def on_ready():
    print(f'Bot logged in as {client.user}')


@client.event
async def on_message(message):
    print(message.content)
    if message.author == client.user:
        return

    if message.content.startswith('$commands'):
        subcommand = message.content.split(' ')[1]

        if subcommand == 'list':
            await message.channel.send(handler.list_commands())

        if subcommand == 'remove':
            try:
                command_id = message.content.split(' ')[2]
                response = handler.remove_command(command_id)
            except IndexError:
                response = 'Please provide id of the command to remove'

            await message.channel.send(response)

    if 'weed' in message.content:
        weed_emoji = discord.utils.get(message.guild.emojis, name='weed')
        print(weed_emoji)
        await message.add_reaction(weed_emoji)


def main():
    load_dotenv()
    token = os.environ.get('BOT_TOKEN')
    client.run(token)


if __name__ == '__main__':
    main()
