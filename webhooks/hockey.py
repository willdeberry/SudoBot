
import dateutil.parser
import pytz
import requests


class Hockey:
    base_url = 'https://statsapi.web.nhl.com'

    def tbl_next_game(self):
        data = requests.get(f'{self.base_url}/api/v1/teams/14?expand=team.schedule.next').json()
        next_game = data['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]
        next_game_date = next_game['gameDate']
        game_time_utc = dateutil.parser.parse(next_game_date)
        game_time_est = game_time_utc.astimezone(pytz.timezone('America/New_York'))
        teams = next_game['teams']
        venue = next_game['venue']['name']
        versus = 'Unknown'

        if teams['away']['team']['id'] != 14:
            versus = teams['away']['team']['name']

        if teams['home']['team']['id'] != 14:
            versus = teams['home']['team']['name']

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
                                "value": f"{game_time_est.strftime('%D %H:%M')} vs {versus}"
                            },
                            {
                                "name": "Venue",
                                "value": f"{venue}"
                            }
                        ]
                    }
                ],
                "allowed_mentions": []
            }
        }

    def tbl_record(self):
        data = requests.get(f'{self.base_url}/api/v1/teams/14?expand=team.stats').json()
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
                                "name": "GP | W-L-O | PTS",
                                "value": f'{games_played} | {wins}-{losses}-{ot} | {points}'
                            }
                        ]
                    }
                ],
                "allowed_mentions": []
            }
        }

    def tbl_score(self):
        data = requests.get(f'{self.base_url}/api/v1/schedule?expand=schedule.linescore&teamId=14').json()

        try:
            game = data['dates'][0]['games'][0]
        except IndexError:
            return self.no_game()

        game_status = game['status']['detailedState']

        if 'In Progress' not in game_status:
            return self.no_game()

        home_team = game['teams']['home']
        home_score = home_team['score']
        home_name = self.get_team_name(home_team)
        away_team = game['teams']['away']
        away_score = away_team['score']
        away_name = self.get_team_name(away_team)

        return {
            "type": 3,
            "data": {
                "tts": False,
                "content": "",
                "embeds": [
                    {
                        "title": "TBL game in progress",
                        "type": "rich",
                        "fields": [
                            {
                                "name": "Current Score",
                                "value": f'{home_name} {home_score} - {away_score} {away_name}'
                            }
                        ]
                    }
                ],
                "allowed_mentions": []
            }
        }


    def no_game(self):
        return {
            "type": 3,
            "data": {
                "tts": False,
                "content": "",
                "embeds": [
                    {
                        "title": "TBL Score",
                        "type": "rich",
                        "fields": [
                            {
                                "name": "No game in progress",
                                "value": 'N/A'
                            }
                        ]
                    }
                ],
                "allowed_mentions": []
            }
        }

    def get_team_name(self, data):
        api = data['team']['link']
        url = f'{self.base_url}/{api}'
        team_data = requests.get(url).json()
        return team_data['teams'][0]['abbreviation']

