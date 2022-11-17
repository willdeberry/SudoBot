
from datetime import datetime
import requests
from time import sleep

from logger import logger


class HockeyGame:
    initialized = False
    scheduled_game = False
    _base_url = 'https://statsapi.web.nhl.com'
    status = {
        'goal': False,
        'scheduled': False,
        'start': False
    }
    score = {
        'home': {
            'name': None,
            'score': None
        },
        'away': {
            'name': None,
            'score': None
        }
    }

    def did_score(self):
        self.status['goal'] = False
        self.status['start'] = False
        today = datetime.now().strftime('%Y-%m-%d')

        try:
            data = requests.get(f'{self._base_url}/api/v1/schedule?expand=schedule.linescore&date={today}&teamId=14').json()
        except requests.exceptions.ConnectionError:
            logger.error('Connection Error')
            return self.status

        try:
            game = data['dates'][0]['games'][0]
        except IndexError:
            self._reset_score()
            return self.status
        except:
            sleep(10)

        game_status = game['status']['detailedState']

        match game_status:
            case 'Scheduled':
                return self._report_scheduled(game['link'])
            case 'In Progress':
                home_team = game['teams']['home']
                away_team = game['teams']['away']

                return self._report_in_progress(home_team, away_team)
            case _:
                if not self.initialized:
                    logger.info('No game scheduled')

                self.initialized = True
                self._reset_score()
                return self.status

    def format_score(self):
        home = self.score['home']
        away = self.score['away']

        return {
                'home': {'name': home['name'], 'score': home['score']},
                'away': {'name': away['name'], 'score': away['score']}
               }

    def _get_team_name(self, data):
        api = data['team']['link']
        url = f'{self._base_url}/{api}'
        team_data = requests.get(url).json()
        return team_data['teams'][0]['abbreviation']

    def _report_in_progress(self, home_team, away_team):
        logger.info('Game currently in progress')

        if self.score['home']['score'] is None or self.score['away']['score'] is None:
            logger.warning('Scoreboard initialized')
            self.status['start'] = True
            self.score['home']['score'] = home_team['score']
            self.score['away']['score'] = away_team['score']

        if home_team['score'] != self.score['home']['score'] or away_team['score'] != self.score['away']['score']:
            logger.info('goal scored!!')
            self.status['goal'] = True
            self.score['home']['score'] = home_team['score']
            self.score['away']['score'] = away_team['score']

            self.score['home']['name'] = self._get_team_name(home_team)
            self.score['away']['name'] = self._get_team_name(away_team)

        return self.status

    def _report_scheduled(self, url):
        if not self.status['scheduled']:
            logger.info('Game scheduled today')

        self.status['scheduled'] = True
        return self.status

    def _reset_score(self):
        self.status['goal'] = False
        self.status['scheduled'] = False
        self.status['start'] = False
        self.score['home']['name'] = None
        self.score['home']['score'] = None
        self.score['away']['name'] = None
        self.score['away']['score'] = None

