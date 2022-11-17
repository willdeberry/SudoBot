
from datetime import datetime
import dateutil.parser
import pytz
import requests
from time import sleep

from logger import logger


class HockeyGame:
    _initialized = False
    _base_url = 'https://statsapi.web.nhl.com'
    status = {
        'goal': False,
        'scheduled': False,
        'start': False
    }
    game_data = {
        'broadcasts': ['N/A'],
        'home': {
            'id': None,
            'name': None,
            'score': None,
            'record': None
        },
        'away': {
            'id': None,
            'name': None,
            'score': None,
            'record': None
        },
        'time': None,
        'venue': None
    }

    def did_score(self):
        self.status['goal'] = False
        today = datetime.now().strftime('%Y-%m-%d')

        try:
            data = requests.get(f'{self._base_url}/api/v1/schedule?&expand=schedule.broadcasts&expand=schedule.linescore&date={today}&teamId=14').json()
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
            case 'In Progress':
                home_team = game['teams']['home']
                away_team = game['teams']['away']

                return self._report_in_progress(home_team, away_team)
            case _:
                if not self._initialized:
                    logger.info('No game scheduled')

                self._initialized = True
                self._reset_game_data()
                return self.status

    def format_score(self):
        home = self.game_data['home']
        away = self.game_data['away']

        return {
                'home': {'name': home['name'], 'score': home['score']},
                'away': {'name': away['name'], 'score': away['score']}
               }

    def get_game_data(self):
        return self.game_data

    def _get_team_name(self, data):
        api = data['team']['link']
        url = f'{self._base_url}/{api}'
        team_data = requests.get(url).json()
        return team_data['teams'][0]['abbreviation']

    def _report_in_progress(self, home_team, away_team):
        logger.info('Game currently in progress')

        if not self.status['start']:
            logger.warning('Scoreboard initialized')
            self.status['start'] = True
            self.game_data['home']['score'] = home_team['score']
            self.game_data['away']['score'] = away_team['score']

        if home_team['score'] != self.game_data['home']['score'] or away_team['score'] != self.game_data['away']['score']:
            logger.info('goal scored!!')
            self.status['goal'] = True
            self.game_data['home']['score'] = home_team['score']
            self.game_data['away']['score'] = away_team['score']

            self.game_data['home']['name'] = self._get_team_name(home_team)
            self.game_data['away']['name'] = self._get_team_name(away_team)

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
        self.status['goal'] = False
        self.status['scheduled'] = False
        self.status['start'] = False
        self.game_data['home']['name'] = None
        self.game_data['home']['score'] = None
        self.game_data['away']['name'] = None
        self.game_data['away']['score'] = None

