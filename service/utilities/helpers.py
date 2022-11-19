
import discord


def build_embed(title, fields, inline = True):
    embed = discord.Embed(title = title, type = 'rich')

    for field in fields:
        embed.add_field(name = field['name'], value = field['value'], inline = inline)

    return embed
