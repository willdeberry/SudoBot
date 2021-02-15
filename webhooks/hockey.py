
import requests


class Hockey:

    def tbl_next_game(self):
        data = requests.get('https://statsapi.web.nhl.com/api/v1/teams/14?expand=team.schedule.next').json()
        next_game = data['teams'][0]['nextGameSchedule']['dates'][0]['date']
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
                                "value": next_game
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
                                "name": "Games Played",
                                "value": games_played
                            },
                            {
                                "name": "Wins",
                                "value": wins
                            },
                            {
                                "name": "Losses",
                                "value": losses
                            },
                            {
                                "name": "OT",
                                "value": ot
                            },
                            {
                                "name": "Points",
                                "value": points
                            }
                        ]
                    }
                ],
                "allowed_mentions": []
            }
        }
