
import discord
from discord.ext import tasks

from sports.hockey_game import HockeyGame


class HockeyUpdates:
    hockey_game = HockeyGame()
    game_status = {}

    def __init__(self, guild, sports_channel):
        self.guild = guild
        self.sports_channel = sports_channel

    @tasks.loop(seconds = 5)
    async def check_score(self):
        game = self.hockey_game.did_score()

        if game['scheduled'] and game['scheduled'] != self.game_status.get('scheduled'):
            await self._report_game_scheduled()

        if game['start'] and game['start'] != self.game_status.get('start'):
            await self._report_game_start()

        if game['goal']:
            await self._report_score()

        if not self.game_status:
            self.game_status = game

    def _find_emoji_in_guild(self, name):
        emojis = self.guild.emojis

        for emoji in emojis:
            if emoji.name != name.lower():
                continue

            return emoji

    def _build_embed(self, title, fields, inline = True):
        embed = discord.Embed(title = title, type = 'rich')

        for field in fields:
            embed.add_field(name = field['name'], value = field['value'], inline = inline)

        return embed

    async def _report_score(self):
        data = self.hockey_game.get_game_data()
        home = data['home']
        away = data['away']
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
