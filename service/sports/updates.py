
import discord
from discord.ext import tasks
import json
import redis

from sports.hockey_game import HockeyGame
from utilities.helpers import build_embed
from utilities.logger import logger


class HockeyUpdates:
    hockey_game = HockeyGame()
    game_status = {}
    _db = redis.Redis(host='redis', port=6379, decode_responses=True)
    db_entries = ['report_game_scheduled', 'report_game_start', 'report_game_end']

    def __init__(self, guild, general_channel, sports_channel):
        self.guild = guild
        self.general_channel = general_channel
        self.sports_channel = sports_channel

        for db_entry in self.db_entries:
            if self._db.exists(db_entry):
                continue

            self._db.set(db_entry, 0)

    @tasks.loop(seconds = 15)
    async def check_score(self):
        game = self.hockey_game.did_score()

        if game['end'] and not self.game_status.get('end') and self.game_status.get('start'):
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
        # If the value is 1 (True), then we don't need to report the game ended again.
        if int(self._db.get('report_game_end')) == 1:
            return

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

        await self._send_to_channel(self.sports_channel, embed = embed)
        self.update_reporting_db('end')

    async def _report_score(self):
        data = self.hockey_game.get_game_data()
        home = data['home']
        away = data['away']
        content = f"Goal Scored: {home['name']} {home['score']} - {away['score']} {away['name']}"

        await self._send_to_channel(self.sports_channel, content = content)

    async def _report_game_scheduled(self):
        # If the value is 1 (True), then we don't need to report the game scheduled again.
        if int(self._db.get('report_game_scheduled')) == 1:
            return

        data = self.hockey_game.get_game_data()
        print(json.dumps(data))
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

        embed = build_embed(f'{goal_emoji} Today is Gameday! {goal_emoji}', fields)

        await self._send_to_channel(self.general_channel, embed = embed)
        self.update_reporting_db('scheduled')

    async def _report_game_start(self):
        # If the value is 1 (True), then we don't need to report the game started again.
        if int(self._db.get('report_game_start')) == 1:
            return

        data = self.hockey_game.get_game_data()
        print(json.dumps(data))
        home_record = data['home']['record']
        home_scratches = ', '.join(data['home']['scratches'])
        away_record = data['away']['record']
        away_scratches = ', '.join(data['away']['scratches'])

        fields = [
                {'name': f"{data['home']['name']} ({home_record})", 'value': f'Scratches: {home_scratches}'},
                {'name': f"{data['away']['name']} ({away_record})", 'value': f'Scratches: {away_scratches}'}
            ]
        embed = build_embed('Game Start', fields)

        await self._send_to_channel(self.sports_channel, embed = embed)
        self.update_reporting_db('start')

    async def _report_intermission(self, period):
        data = self.hockey_game.get_game_data()
        home_name = data['home']['name']
        home_score = data['home']['score']
        home_sog = data['home']['sog']
        away_name = data['away']['name']
        away_score = data['away']['score']
        away_sog = data['away']['sog']

        fields = [
                {'name': home_name, 'value': f'{home_score} ({home_sog} sog)'},
                {'name': away_name, 'value': f'{away_score} ({away_sog} sog)'}
                ]
        embed = build_embed(f'End of {period} period', fields)

        await self._send_to_channel(self.sports_channel, embed = embed)

    async def _send_to_channel(self, channel, content = False, embed = False):
        if content:
            await channel.send(content = content)
            return

        if embed:
            await channel.send(embed = embed)
            return

    def update_reporting_db(self, event):
        match event:
            case 'scheduled':
                self._db.set('report_game_end', 0)
                self._db.set('report_game_scheduled', 1)
                self._db.set('report_game_start', 0)
            case 'start':
                self._db.set('report_game_end', 0)
                self._db.set('report_game_scheduled', 0)
                self._db.set('report_game_start', 1)
            case 'end':
                self._db.set('report_game_end', 1)
                self._db.set('report_game_scheduled', 0)
                self._db.set('report_game_start', 0)
