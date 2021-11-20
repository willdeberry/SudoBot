
import dateutil.parser
import pytz
import requests

from helpers import build_message


class Football:
    _base_url = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl'

    def bucs_next_game(self):
        data = requests.get(f'{self._base_url}/teams/27').json()
        next_game = data['team']['nextEvent'][0]
        tv_channels = next_game['competitions'][0]['broadcasts'][0]['media']['shortName']
        teams = next_game['name']
        next_game_date = next_game['date']
        game_time_utc = dateutil.parser.parse(next_game_date)
        game_time_est = game_time_utc.astimezone(pytz.timezone('America/New_York'))
        venue = next_game['competitions'][0]['venue']['fullName']

        if not tv_channels:
            tv_channels = 'Unavailable'

        fields = [
            {'name': 'Date', 'value': f"{game_time_est.strftime('%D %H:%M')} @ {venue}"},
            {'name': 'Matchup', 'value': f'{teams}'},
            {'name': 'Broadcasts', 'value': tv_channels, 'inline': True},
            {'name': 'Streams', 'value': '[CrackStreams](http://crackstreams.biz/nflstreams/)', 'inline': True}
        ]

        return build_message("Next Game", fields)

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

        fields = [
            {'name': 'Games Played', 'value': games_played, 'inline': True},
            {'name': 'Record', 'value': record, 'inline': True}
        ]

        return build_message("Buc's Record", fields)
