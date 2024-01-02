
import discord
from discord.ext import tasks
import json
import logging
import redis

from sports.hockey_game import HockeyGame
from utilities.helpers import build_embed


logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)


class HockeyUpdates:
    hockey_game = HockeyGame()

    def __init__(self, guild, general_channel, sports_channel):
        self.guild = guild
        self.general_channel = general_channel
        self.sports_channel = sports_channel
        self._db = redis.Redis(host='redis', port=6379, decode_responses=True)

    @tasks.loop(seconds = 15)
    async def check_score(self):
        game = self.hockey_game.poll()
        logging.warning(f'game status: {game}')

        match game:
            case 'scheduled':
                logging.info('reporting game scheduled')
                await self._report_game_scheduled()
            case 'start':
                logging.info('reporting game start')
                await self._report_game_start()
            case 'goal':
                await self._report_score()
            case 'intermission':
                logging.info('reporting intermission')
                await self._report_intermission(game['period'])
            case 'end':
                logging.info('reporting end of game')
                await self._report_end()
            case _:
                self._update_reporting_db('reset')

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

        fields = [
                {'name': home['name'], 'value': f'{home_score} ({home_sog} sog)'},
                {'name': away['name'], 'value': f'{away_score} ({away_sog} sog)'}
                ]
        embed = build_embed('Game End', fields)

        await self._send_to_channel(self.sports_channel, embed = embed)
        self._update_reporting_db('end')

    async def _report_score(self):
        data = self.hockey_game.get_goal_data()
        home_name = data['home']['name']
        home_sore = data['home']['score']
        away_name = data['away']['name']
        away_sore = data['away']['score']
        time_remaining = data['time_remaining']

        content = f"Goal Scored: {home_name} {home_score} - {away_score} {away_name} w/ {time_remaining} left"

        await self._send_to_channel(self.sports_channel, content = content)

    async def _report_game_scheduled(self):
        # If the value is 1 (True), then we don't need to report the game scheduled again.
        if int(self._db.get('report_game_scheduled')) == 1:
            return

        data = self.hockey_game.get_scheduled_data()

        logging.debug(f'scheduled data: {json.dumps(data)}')

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
        self._update_reporting_db('scheduled')

    async def _report_game_start(self):
        # If the value is 1 (True), then we don't need to report the game started again.
        if int(self._db.get('report_game_start')) == 1:
            return

        data = self.hockey_game.get_start_data()

        logging.debug(f'start data: {json.dumps(data)}')

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
        self._update_reporting_db('start')

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

    def _update_reporting_db(self, event):
        match event:
            case 'scheduled':
                self._db.set('report_game_end', 0)
                self._db.set('report_game_scheduled', 1)
                self._db.set('report_game_start', 0)
            case 'start':
                self._db.set('report_game_end', 0)
                self._db.set('report_game_scheduled', 1)
                self._db.set('report_game_start', 1)
            case 'end':
                self._db.set('report_game_end', 1)
                self._db.set('report_game_scheduled', 1)
                self._db.set('report_game_start', 1)
            case 'reset':
                self._db.set('report_game_end', 0)
                self._db.set('report_game_scheduled', 0)
                self._db.set('report_game_start', 0)
