
import dateutil.parser
import pytz
import requests

from utilities.logger import logger


class FootballGame:
    _base_url = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl'

    def bucs_next_game(self):
        data = requests.get(f'{self._base_url}/teams/27').json()
        next_event = data['team']['nextEvent']

        if not next_event:
            return None

        game = next_event[0]
        tv_channels = game['competitions'][0]['broadcasts'][0]['media']['shortName']
        next_game['matchup'] = game['name']
        game_time_utc = dateutil.parser.parse(game['date'])
        game_time_est = game_time_utc.astimezone(pytz.timezone('America/New_York'))
        next_game['time'] = game_time_est.strftime('%D %H:%M'),
        next_game['venue'] = game['competitions'][0]['venue']['fullName']

        if not tv_channels:
            tv_channels = 'Unavailable'

        next_game = {
                'broadcasts': tv_channels,
                'matchup': teams,
                'streams': '[CrackStreams](http://crackstreams.biz/nflstreams/)',
                'time': game_time_est.strftime('%D %H:%M'),
                'venue': venue
                }

        next_game['broadcasts'] = tv_channels

        return next_game

    def bucs_record(self):
        games_played = int(0)
        record = '0-0'

        data = requests.get(f'{self._base_url}/teams/27').json()
        recordData = data['team']['record']['items']

        for item in recordData:
            if item['type'] != 'total':
                continue

            record = item['summary']
            stats = item['stats']

            for stat in stats:
                if stat['name'] != 'gamesPlayed':
                    continue

                games_played = int(stat['value'])

        record = {
                'games_played': games_played,
                'record': record
                }

        return record
