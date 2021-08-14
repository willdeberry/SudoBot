
import dateutil.parser
import pytz
import requests

from helpers import build_message


class Football:
    _base_url = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl'

    def bucs_next_game(self):
        data = requests.get(f'{self._base_url}/teams/27').json()
        next_game = data['team']['nextEvent'][0]
        tv_channels = next_game['competitions'][0]['broadcasts']
        teams = next_game['shortName']
        next_game_date = next_game['date']
        game_time_utc = dateutil.parser.parse(next_game_date)
        game_time_est = game_time_utc.astimezone(pytz.timezone('America/New_York'))
        venue = next_game['competitions'][0]['venue']['fullName']

        if not tv_channels:
            tv_channels = 'Unavailable'

        fields = [
            {'name': 'Date', 'value': f"{game_time_est.strftime('%D %H:%M')} {teams}"},
            {'name': 'Venue', 'value': f'{venue}'},
            {'name': 'Broadcasts', 'value': tv_channels}
        ]

        return build_message("Next Buc's Game", fields)

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

        fields = [{'name': 'GP | W-L', 'value': f'{games_played} | {record}'}]

        return build_message("Buc's Current Record", fields)