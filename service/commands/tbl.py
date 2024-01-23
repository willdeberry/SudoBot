
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
        self.client = NHLClient(verbose = False)
        self.tn_url = 'https://w7.pngwing.com/pngs/515/727/png-transparent-tampa-bay-lightning-national-hockey-league-tampa-bay-rays-tampa-bay-buccaneers-2015-stanley-cup-finals-bay-miscellaneous-blue-game.png'

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
        embed.set_thumbnail(url = self.tn_url)

        await ctx.response.send_message(embed = embed)

    @app_commands.command(description = 'Current record')
    async def record(self, ctx):
        details = self._fetch_record()
        wins = details['wins']
        losses = details['losses']
        ot = details['otLosses']
        l10wins = details['l10Wins']
        l10losses = details['l10Losses']
        l10ot = details['l10OtLosses']
        position = details['divisionSequence']
        position_suffix = self._return_suffix(position)
        wildcard = details['wildcardSequence']
        wildcard_suffix = self._return_suffix(wildcard)

        fields = [
                {'name': 'Games Played', 'value': details['gamesPlayed'], 'inline': True},
                {'name': 'Pos/WC', 'value': f'{position}{position_suffix}/{wildcard}{wildcard_suffix}', 'inline': True},
                {'name': 'Record', 'value': f'{wins}-{losses}-{ot}', 'inline': True},
                {'name': 'Points', 'value': details['points'], 'inline': True},
                {'name': 'Goal Diff', 'value': details['goalDifferential'], 'inline': True},
                {'name': 'Point %', 'value': round(details['pointPctg'], 3), 'inline': True},
                {'name': 'Last 10', 'value': f'{l10wins}-{l10losses}-{l10ot}', 'inline': True},
                {'name': 'Streak', 'value': f'{details["streakCode"]}{details["streakCount"]}', 'inline': True}
            ]
        embed = build_embed("TBL's Record", fields)
        embed.set_thumbnail(url = self.tn_url)

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
        embed =  build_embed('Current Score', fields)
        embed.set_thumbnail(url = self.tn_url)

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
        versus = game['awayTeam']['placeName']['default']
        team_abbrev = game['awayTeam']['abbrev']

        if team_abbrev.lower() == self.name:
            versus = game['homeTeam']['placeName']['default']

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

    def _return_suffix(self, position):
        match position:
            case 1:
                return 'st'
            case 2:
                return 'nd'
            case 3:
                return 'rd'
            case _:
                return 'th'
