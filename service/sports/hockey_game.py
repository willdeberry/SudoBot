
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

        self.poll_status = {
                'status': None,
            }

        self.db.delete('status')

    def poll(self):
        if self.scheduled():
            self.poll_status['status'] = 'scheduled'

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

        self._fetch_standings()
        standings = json.loads(self.db.get('standings'))

        for team in standings:
            team_abbrev = team['teamAbbrev']['default']

            if team_abbrev == data['home']['name']:
                hwins = team['wins']
                hloss = team['losses']
                hot = team['otLosses']

                data['home']['record'] = f'{hwins}-{hloss}-{hot}'

            if team_abbrev == data['away']['name']:
                awins = team['wins']
                aloss = team['losses']
                aot = team['otLosses']

                data['away']['record'] = f'{awins}-{aloss}-{aot}'

        return data

    def _fetch_schedule(self):
        today = str(date.today())
        schedule = self.client.schedule.get_schedule_by_team_by_week(team_abbr = 'TBL')

        self.db.set('schedule', json.dumps(schedule))
        self.db.set('schedule_fetched', today)

    def _fetch_standings(self):
        standings = self.client.standings.get_standings()['standings']
        self.db.set('standings', json.dumps(standings))
