
import dateutil.parser
import pytz
import requests


class Hockey:

    def tbl_next_game(self):
        data = requests.get('https://statsapi.web.nhl.com/api/v1/teams/14?expand=team.schedule.next').json()
        next_game = data['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]
        next_game_date = next_game['gameDate']
        game_time_utc = dateutil.parser.parse(next_game_date)
        game_time_est = game_time_utc.astimezone(pytz.timezone('America/New_York'))
        venue = next_game['venue']['name']

        return {
            "type": 3,
            "data": {
                "tts": False,
                "content": "",
                "embeds": [
                    {
                        "title": "Next TBL Game",
                        "type": "rich",
                        "fields": [
                            {
                                "name": "Date",
                                "value": f"{game_time_est.strftime('%D %H:%M')} @ {venue}"
                            }
                        ]
                    }
                ],
                "allowed_mentions": []
            }
        }

    def tbl_record(self):
        data = requests.get('https://statsapi.web.nhl.com/api/v1/teams/14?expand=team.stats').json()
        stats = data['teams'][0]['teamStats'][0]['splits'][0]['stat']
        games_played = stats['gamesPlayed']
        wins = stats['wins']
        losses = stats['losses']
        ot = stats['ot']
        points = stats['pts']

        return {
            "type": 3,
            "data": {
                "tts": False,
                "content": "",
                "embeds": [
                    {
                        "title": "TBL Current Record",
                        "type": "rich",
                        "fields": [
                            {
                                "name": "Games Played / Points",
                                "value": f'{games_played} / {points}'
                            },
                            {
                                "name": "Record",
                                "value": f'{wins}-{losses}-{ot}'
                            }
                        ]
                    }
                ],
                "allowed_mentions": []
            }
        }
