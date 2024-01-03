
from datetime import date, datetime
import dateutil.parser
import discord
from discord import app_commands
from nhlpy import NHLClient
import pytz

from utilities.helpers import build_embed


class TBLCommands(app_commands.Group):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'tbl'
        self.client = NHLClient()

    @app_commands.command(description = 'Next scheduled game')
    async def next(self, ctx):
        details = self._fetch_next_game()
        fields = [
                {'name': 'Date', 'value': f"{details['time']} @ {details['venue']}"},
                {'name': 'Versus', 'value': details['versus']},
                {'name': 'Broadcasts', 'value': details['broadcasts'], 'inline': True},
                {'name': 'Streams', 'value': details['streams'], 'inline': True}
            ]
        embed = build_embed('Next Game', fields)

        await ctx.response.send_message(embed = embed)

    @app_commands.command(description = 'Current record')
    async def record(self, ctx):
        details = self._fetch_record()
        fields = [
                {'name': 'Games Played', 'value': details['gamesPlayed']},
                {'name': 'Wins', 'value': details['wins'], 'inline': True},
                {'name': 'Losses', 'value': details['losses'], 'inline': True},
                {'name': 'OT Losses', 'value': details['otLosses'], 'inline': True},
                {'name': 'Points', 'value': details['points']}
            ]
        embed = build_embed("TBL's Record", fields)

        await ctx.response.send_message(embed = embed)

    @app_commands.command(description = 'Current score of game if one is in progress')
    async def score(self, ctx):
        details = self._fetch_score()

        if not details:
            await ctx.response.send_message('No game in progress.')
            return

        home = details['homeTeam']
        away = details['awayTeam']
        fields = [{'name': 'Game', 'value': f"{home['abbrev']} {home['score']} - {away['score']} {away['abbrev']}"}]
        return build_message('Current Score', fields)
        await ctx.response.send_message(embed = embed)

    def _fetch_next_game(self):
        today = str(date.today())
        schedule = self.client.schedule.get_schedule_by_team_by_week(self.name)

        next_date = sorted([game['gameDate'] for game in schedule if game['gameDate'] >= today])[0]
        game = [game for game in schedule if game['gameDate'] == next_date][0]

        game_time_utc = dateutil.parser.parse(game['startTimeUTC'])
        game_time_est = game_time_utc.astimezone(pytz.timezone('America/New_York'))
        game_time = game_time_est.strftime('%D %H:%M')
        broadcasts = [broadcast['network'] for broadcast in game['tvBroadcasts']]
        versus = game['awayTeam']['abbrev']

        if versus.lower() == self.name:
            versus = game['homeTeam']['abbrev']

        return {
                'time': game_time,
                'venue': game['venue']['default'],
                'versus': versus,
                'broadcasts': ', '.join(broadcasts),
                'streams': '[CastStreams](https://www.caststreams.com/), [CrackStreams](http://crackstreams.biz/nhlstreams/)'
            }

    def _fetch_record(self):
        standings = self.client.standings.get_standings()['standings']

        for standing in standings:
            if standing['teamAbbrev']['default'].lower() != self.name:
                continue

            return standing

    def _fetch_score(self):
        all_games = self.client.game_center.client.get(f'scoreboard/{self.name}/now').json()['gamesByDate']
        today = date.today()
        todays_games = []

        if not all_games:
            return False

        for games in all_games:
            game_date = datetime.strptime(games['date'], '%Y-%m-%d').date()

            if game_date != today:
                continue

            todays_games = games['games']

        if not todays_games:
            return False

        for game in todays_games:
            state = game['gameState']

            if state != 'OK':
                continue

            return game

        return False
