import requests


class Hockey:

    def tbl_next_game(self):
        data = requests.get('https://statsapi.web.nhl.com/api/v1/teams/14?expand=team.schedule.next').json()
        next_game = data['teams'][0]['nextGameSchedule']['dates'][0]['date']
        return f'**Next TBL game is** {next_game}'

    def tbl_record(self):
        data = requests.get('https://statsapi.web.nhl.com/api/v1/teams/14?expand=team.stats').json()
        stats = data['teams'][0]['teamStats'][0]['splits'][0]['stat']
        games_played = stats['gamesPlayed']
        wins = stats['wins']
        losses = stats['losses']
        ot = stats['ot']
        points = stats['pts']

        return f'**TBL Games played**: {games_played} **Standings**: {wins}-{losses}-{ot} **Points**: {points}'

