
import requests

from logger import logger


class HockeyGame:
    _base_url = 'https://statsapi.web.nhl.com'
    status = {
        'goal': False,
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
        data = requests.get(f'{self._base_url}/api/v1/schedule?expand=schedule.linescore&teamId=14').json()

        try:
            game = data['dates'][0]['games'][0]
        except IndexError:
            logger.warning('No game scheduled today')
            self._reset_score()
            return self.status

        game_status = game['status']['detailedState']

        if 'In Progress' not in game_status:
            self._reset_score()
            return self.status

        home_team = game['teams']['home']
        away_team = game['teams']['away']

        if self.score['home']['score'] is None or self.score['away']['score'] is None:
            logger.warning('Scoreboard initialized')
            self.status['start'] = True
            self.score['home']['score'] = home_team['score']
            self.score['away']['score'] = away_team['score']
            return self.status


        if home_team['score'] != self.score['home']['score'] or away_team['score'] != self.score['away']['score']:
            logger.info('goal scored!!')
            self.status['goal'] = True
            self.score['home']['score'] = home_team['score']
            self.score['away']['score'] = away_team['score']

            self.score['home']['name'] = self._get_team_name(home_team)
            self.score['away']['name'] = self._get_team_name(away_team)

        return self.status


    def format_score(self):
        home = self.score['home']
        away = self.score['away']

        return f"{home['name']} {home['score']} - {away['score']} {away['name']}"

    def _get_team_name(self, data):
        api = data['team']['link']
        url = f'{self._base_url}/{api}'
        team_data = requests.get(url).json()
        return team_data['teams'][0]['abbreviation']

    def _reset_score(self):
        self.status['goal'] = False
        self.status['start'] = False
        self.score['home']['name'] = None
        self.score['home']['score'] = None
        self.score['away']['name'] = None
        self.score['away']['score'] = None

