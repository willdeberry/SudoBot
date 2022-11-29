
import discord
from discord.ext import tasks

from sports.hockey_game import HockeyGame
from utilities.helpers import build_embed
from utilities.logger import logger


class HockeyUpdates:
    hockey_game = HockeyGame()
    game_status = {}

    def __init__(self, guild, sports_channel):
        self.guild = guild
        self.sports_channel = sports_channel

    @tasks.loop(seconds = 5)
    async def check_score(self):
        game = self.hockey_game.did_score()

        if game['end'] and not self.game_status.get('end'):
            logger.info('reporting end of game')
            await self._report_end()

        if game['scheduled'] and not self.game_status.get('scheduled'):
            logger.info('reporting game scheduled')
            await self._report_game_scheduled()

        if game['start'] and not self.game_status.get('start'):
            logger.info('reporting game start')
            await self._report_game_start()

        if game['intermission'] and not self.game_status.get('intermission'):
            logger.info('reporting intermission')
            await self._report_intermission(game['period'])

        if game['goal']:
            await self._report_score()

        self.game_status = game.copy()

    def _find_emoji_in_guild(self, name):
        emojis = self.guild.emojis

        for emoji in emojis:
            if emoji.name != name.lower():
                continue

            return emoji

    async def _report_end(self):
        data = self.hockey_game.get_game_data()
        home = data['home']
        away = data['away']

        home_score = home['score']
        home_sog = home['sog']
        away_score = away['score']
        away_sog = away['sog']
        #stars = ', '.join(data['stars'])
        #winning_goalie = data['goalies']['winning']
        #losing_goalie = data['goalies']['losing']

        fields = [
                {'name': home['name'], 'value': f'{home_score} ({home_sog} sog)'},
                {'name': away['name'], 'value': f'{away_score} ({away_sog} sog)'},
                #{'name': 'Winning Goalie', 'value': winning_goalie},
                #{'name': 'Losing Goalie', 'value': losing_goalie},
                #{'name': '3 Stars', 'value': stars}
                ]
        embed = build_embed('Game End', fields)

        await self.sports_channel.send(embed = embed)

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

        embed = build_embed(f'{goal_emoji} Today is Gameday! {goal_emoji}', fields, inline = False)

        await self.sports_channel.send(embed = embed)

    async def _report_game_start(self):
        tbl_emoji = self._find_emoji_in_guild('tbl')

        fields = [{'name': f'{tbl_emoji}', 'value': 'Time to tune in!'}]
        embed = build_embed('Game Start', fields, inline = False)

        await self.sports_channel.send(embed = embed)

    async def _report_intermission(self, period):
        data = self.hockey_game.get_game_data()
        home_name = data['home']['name']
        home_score = data['home']['score']
        home_sog = data['home']['sog']
        away_name = data['away']['name']
        away_score = data['away']['score']
        away_sog = data['away']['sog']

        fields = [
                {'name': home_name, 'value': f'Goals: {home_score} ({home_sog} sog)'},
                {'name': away_name, 'value': f'Goals: {away_score} ({away_sog} sog)'}
                ]
        embed = build_embed(f'End of {period} period', fields)

        await self.sports_channel.send(embed = embed)
