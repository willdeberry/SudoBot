
from datetime import datetime
import dateutil.parser
import pytz
import requests
from time import sleep

from utilities.logger import logger


class HockeyGame:
    _initialized = False
    _base_url = 'https://statsapi.web.nhl.com'
    status = {
            'end': False,
            'goal': False,
            'intermission': False,
            'scheduled': False,
            'start': False
        }
    game_data = {
            'away': {
                'id': None,
                'name': None,
                'score': None,
                'sog': None,
                'record': None
            },
            'broadcasts': ['N/A'],
            'goalies': {
                'winning': None,
                'losing': None
            },
            'home': {
                'id': None,
                'name': None,
                'score': None,
                'sog': None,
                'record': None
            },
            'period': None,
            'stars': [],
            'time': None,
            'venue': None
        }

    def did_score(self):
        self.status['goal'] = False

        try:
            data = requests.get(f'{self._base_url}/api/v1/schedule?&expand=schedule.broadcasts&expand=schedule.linescore&teamId=14').json()
        except requests.exceptions.ConnectionError:
            logger.error('Connection Error')
            return self.status

        try:
            game = data['dates'][0]['games'][0]
        except IndexError:
            self._reset_game_data()
            return self.status
        except:
            sleep(10)

        game_status = game['status']['detailedState']

        match game_status:
            case 'Scheduled':
                return self._report_scheduled(game)
            case 'In Progress' | 'In Progress - Critical':
                home_team = game['linescore']['teams']['home']
                away_team = game['linescore']['teams']['away']
                current_period = game['linescore']['currentPeriodOrdinal']
                intermission = True if game['linescore']['currentPeriodTimeRemaining'] == 'END' else False

                if intermission:
                    return self._report_intermission(current_period, home_team, away_team)

                self.status['intermission'] = False
                return self._report_in_progress(home_team, away_team)
            case 'Game Over' | 'Final':
                home_team = game['linescore']['teams']['home']
                away_team = game['linescore']['teams']['away']
                return self._report_end(game['link'], home_team, away_team)
            case _:
                if not self._initialized:
                    logger.info('No game scheduled')

                self._initialized = True
                self._reset_game_data()
                return self.status

    def get_game_data(self):
        return self.game_data

    def tbl_next_game(self):
        data = requests.get(f'{self._base_url}/api/v1/teams/14?expand=team.schedule.next&expand=schedule.broadcasts').json()
        next_game = data['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]
        game_time_utc = dateutil.parser.parse(next_game['gameDate'])
        game_time_est = game_time_utc.astimezone(pytz.timezone('America/New_York'))
        teams = next_game['teams']
        tv_channels = ['N/A']
        broadcasts = next_game.get('broadcasts', None)
        versus = 'Unknown'

        if broadcasts:
            tv_channels = []
            for broadcast in broadcasts:
                tv_channels.append(broadcast['name'])

        if teams['away']['team']['id'] != 14:
            versus = teams['away']['team']['name']

        if teams['home']['team']['id'] != 14:
            versus = teams['home']['team']['name']

        next_game = {
                'broadcasts': ', '.join(tv_channels),
                'streams': '[CastStreams](https://www.caststreams.com/), [CrackStreams](http://crackstreams.biz/nhlstreams/)',
                'time': game_time_est.strftime('%D %H:%M'),
                'venue': next_game['venue']['name'],
                'versus': versus,
                }

        return next_game

    def tbl_record(self):
        data = requests.get(f'{self._base_url}/api/v1/teams/14?expand=team.stats').json()
        stats = data['teams'][0]['teamStats'][0]['splits'][0]['stat']
        record = {
                'games_played': stats['gamesPlayed'],
                'losses': stats['losses'],
                'ot': stats['ot'],
                'points': stats['pts'],
                'wins': stats['wins'],
                }

        return record

    def tbl_score(self):
        if not self.status['start']:
            return None

        return self.game_data

    def _get_team_name(self, data):
        api = data['team']['link']
        url = f'{self._base_url}/{api}'
        team_data = requests.get(url).json()
        return team_data['teams'][0]['abbreviation']

    def _no_game(self):
        fields = [{'name': 'No game in progress', 'value': 'N/A'}]
        return build_message('Curent Score', fields)

    def _report_end(self, api, home_team, away_team):
        data = requests.get(f'{self._base_url}{api}').json()
        self.status['intermission'] = False
        self.status['scheduled'] = False
        self.status['start'] = False
        self.status['end'] = True

        results = data['liveData']['decisions']
       # self.game_data['goalies']['winning'] = results['winner']['fullName']
       # self.game_data['goalies']['losing'] = results['loser']['fullName']
       # self.game_data['stars'].append(results['firstStar']['fullName'])
       # self.game_data['stars'].append(results['secondStar']['fullName'])
       # self.game_data['stars'].append(results['thirdStar']['fullName'])
        self.game_data['home']['name'] = self._get_team_name(home_team)
        self.game_data['home']['score'] = home_team['goals']
        self.game_data['home']['sog'] = home_team['shotsOnGoal']
        self.game_data['away']['name'] = self._get_team_name(away_team)
        self.game_data['away']['score'] = away_team['goals']
        self.game_data['away']['sog'] = away_team['shotsOnGoal']

        return self.status

    def _report_in_progress(self, home_team, away_team):
        logger.info('Game currently in progress')

        if not self.status['start']:
            logger.warning('Scoreboard initialized')
            self.status['start'] = True
            self.status['end'] = False
            self.game_data['home']['score'] = home_team['goals']
            self.game_data['away']['score'] = away_team['goals']

        if home_team['goals'] != self.game_data['home']['score'] or away_team['goals'] != self.game_data['away']['score']:
            logger.info('goal scored!!')
            self.status['goal'] = True
            self.game_data['home']['score'] = home_team['goals']
            self.game_data['away']['score'] = away_team['goals']

            self.game_data['home']['name'] = self._get_team_name(home_team)
            self.game_data['away']['name'] = self._get_team_name(away_team)

        return self.status

    def _report_intermission(self, period, home_team, away_team):
        logger.info('Intermission')
        self.status['intermission'] = True
        self.status['period'] = period
        self.game_data['home']['name'] = self._get_team_name(home_team)
        self.game_data['home']['score'] = home_team['goals']
        self.game_data['home']['sog'] = home_team['shotsOnGoal']
        self.game_data['away']['name'] = self._get_team_name(away_team)
        self.game_data['away']['score'] = away_team['goals']
        self.game_data['away']['sog'] = away_team['shotsOnGoal']

        return self.status

    def _report_scheduled(self, data):
        if not self.status['scheduled']:
            logger.info('Game scheduled today')
            self.status['scheduled'] = True

        team_details = data['teams']
        home_wins = team_details['home']['leagueRecord']['wins']
        home_losses = team_details['home']['leagueRecord']['losses']
        home_ot = team_details['home']['leagueRecord']['ot']
        away_wins = team_details['away']['leagueRecord']['wins']
        away_losses = team_details['away']['leagueRecord']['losses']
        away_ot = team_details['away']['leagueRecord']['ot']

        self.game_data['home']['record'] = f'{home_wins}-{home_losses}-{home_ot}'
        self.game_data['away']['record'] = f'{away_wins}-{away_losses}-{away_ot}'
        self.game_data['venue'] = data['venue']['name']

        game_time_utc = dateutil.parser.parse(data['gameDate'])
        game_time_est = game_time_utc.astimezone(pytz.timezone('America/New_York'))
        self.game_data['time'] = game_time_est.strftime('%D %H:%M')

        self.game_data['home']['name'] = self._get_team_name(team_details['home'])
        self.game_data['away']['name'] = self._get_team_name(team_details['away'])

        self.game_data['broadcasts'] = [broadcast['name'] for broadcast in data['broadcasts'] if data['broadcasts']]

        return self.status

    def _reset_game_data(self):
        self._process_dict(self.status)
        self._process_dict(self.game_data)

    def _process_dict(self, data):
        for key, value in data.items():
            if hasattr(value, 'items'):
                self._process_dict(value)
                continue

            data[key] = None
