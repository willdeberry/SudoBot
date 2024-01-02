
from datetime import date, datetime, timedelta
import dateutil.parser
import json
from nhlpy import NHLClient
import pytz
import redis


class HockeyGame:
    def __init__(self):
        self.client = NHLClient()
        self.db = redis.Redis(host='redis', port=6379, decode_responses=True)

        self.poll_status = None

        self.db.delete('status')

    def poll(self):
        self.poll_status = None

        if self.scheduled():
            self.poll_status = 'scheduled'

        if self.start():
            self.poll_status = 'start'

        if self.goal():
            self.poll_status = 'goal'

        return self.poll_status

    def scheduled(self):
        try:
            if self.db.get('status') == 'scheduled':
                return True
        except TypeError:
            pass

        last_fetch = self.db.get('schedule_fetched')

        if not last_fetch:
            self._fetch_schedule()
            last_fetch = self.db.get('schedule_fetched')

        last_fetch_datetime = datetime.strptime(last_fetch, '%Y-%m-%d').date()
        next_fetch = last_fetch_datetime + timedelta(days=7)
        today = date.today()

        if today >= next_fetch:
            self._fetch_schedule()

        for game in json.loads(self.db.get('schedule')):
            game_date = game['gameDate']
            game_date_datetime = datetime.strptime(game_date, '%Y-%m-%d').date()

            if game_date_datetime != today:
                continue

            self.db.set('status', 'scheduled')
            self.db.set('schedule_game', json.dumps(game))
            return True

        self.db.set('schedule_today', 0)
        return False

    def start(self):
        try:
            if self.db.get('status') == 'start':
                return True
        except TypeError:
            pass

        game_id = json.loads(self.db.get('schedule_game'))['id']
        self._fetch_boxscore(game_id)
        game_state = json.loads(self.db.get('boxscore'))['gameState']

        if game_state != 'OK':
            return False

        return True

    def goal(self):
        cur_home_goals = 0
        cur_away_goals = 0
        game_id = json.loads(self.db.get('schedule_game'))['id']
        self._fetch_boxscore(game_id)
        boxscore = json.loads(self.db.get('boxscore'))
        game_state = boxscore['gameState']

        if game_state != 'OK':
            return False

        if self.db.exists('home_goals'):
            home_goals = self.db.get('home_goals')

        if self.db.exists('away_goals'):
            away_goals = self.db.get('away_goals')

        total_goals = boxscore['linescore']['totals']
        home_goals = total_goals['home']
        away_goals = total_goals['away']

        if home_goals != cur_home_goals or away_goals != cur_away_goals:
            self.db.set('home_goals', home_goals)
            self.db.set('away_goals', away_goals)

            return True

        return False

    def get_scheduled_data(self):
        data = {}
        data['home'] = {}
        data['away'] = {}

        game = json.loads(self.db.get('schedule_game'))
        game_time_utc = dateutil.parser.parse(game['startTimeUTC'])
        game_time_est = game_time_utc.astimezone(pytz.timezone('America/New_York'))
        records = self._get_records(game['homeTeam']['abbrev'], game['awayTeam']['abbrev'])

        data['time'] = game_time_est.strftime('%D %H:%M')
        data['venue'] = game['venue']['default']
        data['broadcasts'] = [broadcast['network'] for broadcast in game['tvBroadcasts']]
        data['home']['name'] = game['homeTeam']['abbrev']
        data['away']['name'] = game['awayTeam']['abbrev']
        data['home']['record'] = records['home']
        data['away']['record'] = records['away']

        return data

    def get_start_data(self):
        data = {}
        data['home'] = {}
        data['away'] = {}

        boxscore = json.loads(self.db.get('boxscore'))
        records = self._get_records(boxscore['homeTeam']['abbrev'], boxscore['awayTeam']['abbrev'])
        game_info = boxscore['boxscore']['gameInfo']['homeTeam']['scratches']
        home_scratches = game_info['homeTeam']['scratches']
        away_scratches = game_info['awayTeam']['scratches']

        data['home']['name'] = boxscore['homeTeam']['abbrev']
        data['away']['name'] = boxscore['awayTeam']['abbrev']
        data['home']['record'] = records['home']
        data['away']['record'] = records['away']
        data['home']['scratches'] = [player['lastName']['default'] for player in home_scratches]
        data['away']['scratches'] = [player['lastName']['default'] for player in away_scratches]

        return data

    def get_goal_data(self):
        data = {}
        data['home'] = {}
        data['away'] = {}

        boxscore = json.loads(self.db.get('boxscore'))

        data['home']['name'] = boxscore['homeTeam']['abbrev']
        data['away']['name'] = boxscore['awayTeam']['abbrev']
        data['home']['score'] = self.db.get('home_goals')
        data['away']['score'] = self.db.get('away_goals')
        data['time_left'] = boxscore['clock']['timeRemaining']

        return data

    def _fetch_schedule(self):
        today = str(date.today())
        schedule = self.client.schedule.get_schedule_by_team_by_week(team_abbr = 'TBL')

        self.db.set('schedule', json.dumps(schedule))
        self.db.set('schedule_fetched', today)

    def _fetch_standings(self):
        standings = self.client.standings.get_standings()['standings']
        self.db.set('standings', json.dumps(standings))

    def _fetch_boxscore(self, game_id):
        boxscore = self.client.game_center.boxscore(game_id = game_id)
        self.db.set('boxscore', json.dumps(boxscore))

    def _get_records(self, home_name, away_name):
        data = {}
        self._fetch_standings()
        standings = json.loads(self.db.get('standings'))

        for team in standings:
            team_abbrev = team['teamAbbrev']['default']

            if team_abbrev == home_name:
                hwins = team['wins']
                hloss = team['losses']
                hot = team['otLosses']

                data['home'] = f'{hwins}-{hloss}-{hot}'

            if team_abbrev == away_name:
                awins = team['wins']
                aloss = team['losses']
                aot = team['otLosses']

                data['away'] = f'{awins}-{aloss}-{aot}'

        return data
