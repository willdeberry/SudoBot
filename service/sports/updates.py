
import discord
from discord.ext import tasks
import logging
import json
import redis

from sports.hockey_game import HockeyGame
from utilities.helpers import build_embed


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class HockeyUpdates:
    hockey_game = HockeyGame()

    def __init__(self, guild, general_channel, sports_channel):
        self.guild = guild
        self.general_channel = general_channel
        self.sports_channel = sports_channel
        self._db = redis.Redis(host='redis', port=6379, decode_responses=True)

    @tasks.loop(seconds = 15)
    async def check_score(self):
        try:
            game = self.hockey_game.poll()
        except Exception:
            import traceback
            logging.error(f'error: {traceback.format_exc()}')
            game = None

        logging.info(f'status: {game}')

        match game:
            case 'scheduled':
                await self._report_game_scheduled()
            case 'start':
                await self._report_game_start()
            case 'goal':
                await self._report_score()
            case 'intermission':
                await self._report_intermission()
            case 'end':
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
            self._update_reporting_db('end')
            return

        logging.info('reporting end of game')

        data = self.hockey_game.get_game_end_data()
        home = data['home']
        away = data['away']

        home_name = home['name']
        home_score = home['score']
        home_sog = home['sog']
        home_fpperc = home['faceoffWinningPctg']
        home_ppconv = home['powerPlay']
        home_hits = home['hits']
        home_blocked = home['blockedShots']
        home_give = home['giveaways']
        home_take = home['takeaways']
        away_name = away['name']
        away_score = away['score']
        away_sog = away['sog']
        away_fpperc = away['faceoffWinningPctg']
        away_ppconv = away['powerPlay']
        away_hits = away['hits']
        away_blocked = away['blockedShots']
        away_give = away['giveaways']
        away_take = away['takeaways']

        fields = [
                {'name': 'Score', 'value': f'{home_name}: {home_score} - {away_score} :{away_name}'},
                {'name': 'Shots on Goal', 'value': f'{home_name}: {home_sog} - {away_sog} :{away_name}', 'inline': True},
                {'name': 'FaceOff %', 'value': f'{home_name}: {home_fpperc} - {away_fpperc} :{away_name}', 'inline': True},
                {'name': 'PP Conversion', 'value': f'{home_name}: {home_ppconv} - {away_ppconv} :{away_name}', 'inline': True},
                {'name': 'Hits', 'value': f'{home_name}: {home_hits} - {away_hits} :{away_name}', 'inline': True},
                {'name': 'Blocked Shots', 'value': f'{home_name}: {home_blocked} - {away_blocked} :{away_name}', 'inline': True},
                {'name': 'Giveaways', 'value': f'{home_name}: {home_give} - {away_give} :{away_name}', 'inline': True},
                {'name': 'Takeaways', 'value': f'{home_name}: {home_take} - {away_take} :{away_name}', 'inline': True}
            ]
        embed = build_embed('Game End', fields)

        await self._send_to_channel(self.sports_channel, embed = embed)
        self._update_reporting_db('end')

    async def _report_score(self):
        data = self.hockey_game.get_goal_data()
        home_name = data['home']['name']
        home_score = data['home']['score']
        away_name = data['away']['name']
        away_score = data['away']['score']
        time_left = data['time_left']
        period = data['period']

        content = f"Goal Scored: {home_name} {home_score} - {away_score} {away_name} w/ {time_left} left in period {period}"

        await self._send_to_channel(self.sports_channel, content = content)

    async def _report_game_scheduled(self):
        # If the value is 1 (True), then we don't need to report the game scheduled again.
        if int(self._db.get('report_game_scheduled')) == 1:
            self._update_reporting_db('scheduled')
            return

        logging.info('reporting game scheduled')

        data = self.hockey_game.get_scheduled_data()
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
                {'name': 'Streams', 'value': '[CrackStreams](http://crackstreams.biz/nhlstreams/)', 'inline': True}
            ]

        embed = build_embed(f'{goal_emoji} Today is Gameday! {goal_emoji}', fields)

        await self._send_to_channel(self.general_channel, embed = embed)
        self._update_reporting_db('scheduled')

    async def _report_game_start(self):
        # If the value is 1 (True), then we don't need to report the game started again.
        if int(self._db.get('report_game_start')) == 1:
            self._update_reporting_db('start')
            return

        logging.info('reporting game start')

        data = self.hockey_game.get_start_data()

        if not data:
            return

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

    async def _report_intermission(self):
        # If the value is 1 (True), then we don't need to report the game started again.
        if int(self._db.get('report_game_intermission')) == 1:
            self._update_reporting_db('intermission')
            return

        logging.info('reporting intermission')

        data = self.hockey_game.get_intermission_data()
        period = data['period']
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
        self._update_reporting_db('intermission')

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
                self._db.set('report_game_intermission', 0)
            case 'start':
                self._db.set('report_game_end', 0)
                self._db.set('report_game_scheduled', 1)
                self._db.set('report_game_start', 1)
                self._db.set('report_game_intermission', 0)
            case 'intermission':
                self._db.set('report_game_end', 0)
                self._db.set('report_game_scheduled', 1)
                self._db.set('report_game_start', 1)
                self._db.set('report_game_intermission', 1)
            case 'end':
                self._db.set('report_game_end', 1)
                self._db.set('report_game_scheduled', 0)
                self._db.set('report_game_start', 1)
                self._db.set('report_game_intermission', 1)
            case 'reset':
                self._db.set('report_game_end', 0)
                self._db.set('report_game_scheduled', 0)
                self._db.set('report_game_start', 0)
                self._db.set('report_game_intermission', 0)
