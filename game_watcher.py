
import requests

from logger import logger


class HockeyGame:
    base_url = 'https://statsapi.web.nhl.com'
    update = False
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

    def reset_score(self):
        self.score['home']['name'] = None
        self.score['home']['score'] = None
        self.score['away']['name'] = None
        self.score['away']['score'] = None

    def did_score(self):
        self.update = False
        data = requests.get(r'{base_url}/api/v1/schedule?expand=schedule.linescore&teamId=14').json()

        try:
            game = data['dates'][0]['games'][0]
        except IndexError:
            logger.warning('No game scheduled today')
            self.reset_score()
            return self.update

        game_status = game['status']['detailedState']

        if game_status != 'In Progress':
            logger.warning('Game not currently in progress')
            self.reset_score()
            return self.update

        home_team = game['teams']['home']
        away_team = game['teams']['away']

        if not self.score['home']['score'] or not self.score['away']['score']:
            logger.warning('Scoreboard initialized')
            self.score['home']['score'] = home_team['score']
            self.score['away']['score'] = away_team['score']
            return self.update


        if home_team['score'] != self.score['home']['score'] or away_team['score'] != self.away_team['score']:
            logger.info('goal scored!!')
            self.score['home']['score'] = home_team['score']
            self.score['away']['score'] = away_team['score']

            self.score['home']['name'] = self.get_team_name(home_team)
            self.score['away']['name'] = self.get_team_name(away_team)
            self.update = True

        logger.info(f"score {self.score['home']['score']} - {self.score['away']['score']}")
        return self.update

    def get_team_name(self, data):
        api = data['team']['link']
        url = f'{base_url}/{api}'
        team_data = requests.get(url).json()
        return team_data[0]['abbreviation']

    def format_score(self):
        home = self.score['home']
        away = self.score['away']

        return f"{home['name']} {home['score']} - {away['score']} {away['name']}"

