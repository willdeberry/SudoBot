
import discord


def build_embed(title, fields):
    embed = discord.Embed(title = title, type = 'rich')

    for field in fields:
        inline = field.get('inline', False)
        embed.add_field(name = field['name'], value = field['value'], inline = inline)

    return embed
