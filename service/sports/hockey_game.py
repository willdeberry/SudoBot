
from datetime import date, datetime, timedelta
import dateutil.parser
import json
from nhlpy import NHLClient
import pytz
import redis


class HockeyGame:
    def __init__(self):
        self.client = NHLClient(verbose = False)
        self.db = redis.Redis(host='redis', port=6379, decode_responses=True)
        self.poll_status = None

        self.db.delete('status')

    def poll(self):
        self.poll_status = None

        self.scheduled()
        self.start()
        self.goal()
        self.intermission()
        self.game_end()

        if self.db.exists('status'):
            self.poll_status = self.db.get('status')

        return self.poll_status

    def scheduled(self):
        today = date.today()
        self._fetch_schedule()

        for game in json.loads(self.db.get('schedule')):
            game_date = game['gameDate']
            game_state = game['gameState']
            game_date_datetime = datetime.strptime(game_date, '%Y-%m-%d').date()

            if game_date_datetime != today:
                continue

            if game_state not in ['FUT','PRE','LIVE']:
                continue

            self.db.set('status', 'scheduled')
            self.db.set('schedule_game', json.dumps(game))
            return

    def start(self):
        if not self.db.exists('schedule_game'):
            return

        schedule_game = json.loads(self.db.get('schedule_game'))
        game_id = schedule_game['id']
        game_state = schedule_game['gameState']

        if game_state != 'LIVE':
            return

        self._fetch_boxscore(game_id)
        self.db.set('status', 'start')

    def goal(self):
        current_status = self.db.get('status')

        if current_status not in ['start', 'scheduled']:
            return

        if not self.db.exists('schedule_game'):
            return

        schedule_game = json.loads(self.db.get('schedule_game'))
        game_state = schedule_game['gameState']

        if game_state != 'LIVE':
            return

        cur_home_goals = 0
        cur_away_goals = 0
        game_id = schedule_game['id']
        self._fetch_boxscore(game_id)
        boxscore = json.loads(self.db.get('boxscore'))

        if self.db.exists('home_goals'):
            cur_home_goals = int(self.db.get('home_goals'))

        if self.db.exists('away_goals'):
            cur_away_goals = int(self.db.get('away_goals'))

        try:
            total_goals = boxscore['summary']['linescore']['totals']
        except KeyError:
            self._fetch_boxscore(game_id)
            total_goals = boxscore['summary']['linescore']['totals']

        home_goals = total_goals['home']
        away_goals = total_goals['away']

        if home_goals != cur_home_goals or away_goals != cur_away_goals:
            self.db.set('home_goals', home_goals)
            self.db.set('away_goals', away_goals)

            try:
                self.db.set('time_scored', boxscore['clock']['timeRemaining'])
                self.db.set('period_scored', boxscore['periodDescriptor']['number'])
            except KeyError:
                self._fetch_boxscore(game_id)
            finally:
                boxscore = json.loads(self.db.get('boxscore'))
                self.db.set('time_scored', boxscore['clock']['timeRemaining'])
                self.db.set('period_scored', boxscore['periodDescriptor']['number'])

            self.db.set('status', 'goal')

    def intermission(self):
        if not self.db.exists('schedule_game'):
            return

        game_id = json.loads(self.db.get('schedule_game'))['id']
        current_status = self.db.get('status')

        if current_status not in ['start', 'scheduled']:
            return

        self._fetch_boxscore(game_id)
        boxscore = json.loads(self.db.get('boxscore'))
        game_state = boxscore['gameState']

        if game_state != 'LIVE':
            return

        if boxscore['clock']['inIntermission']:
            self.db.set('status', 'intermission')

    def game_end(self):
        current_status = self.db.get('status')

        if current_status not in ['start', 'scheduled', 'intermission']:
            return

        boxscore = json.loads(self.db.get('boxscore'))
        game_state = boxscore['gameState']

        if game_state in ['FINAL']:
            self.db.delete('home_goals')
            self.db.delete('away_goals')
            self.db.set('status', 'end')

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

        schedule_game = json.loads(self.db.get('schedule_game'))
        game_id = schedule_game['id']

        boxscore = json.loads(self.db.get('boxscore'))
        records = self._get_records(boxscore['homeTeam']['abbrev'], boxscore['awayTeam']['abbrev'])

        try:
            game_info = boxscore['summary']['gameInfo']
            data['home']['name'] = boxscore['homeTeam']['abbrev']
            data['away']['name'] = boxscore['awayTeam']['abbrev']
        except KeyError:
            self._fetch_boxscore(game_id)
        finally:
            game_info = boxscore['summary']['gameInfo']
            data['home']['name'] = boxscore['homeTeam']['abbrev']
            data['away']['name'] = boxscore['awayTeam']['abbrev']

        home_scratches = game_info['homeTeam']['scratches']
        away_scratches = game_info['awayTeam']['scratches']

        data['home']['record'] = records['home']
        data['away']['record'] = records['away']
        data['home']['scratches'] = [player['lastName']['default'] for player in home_scratches]
        data['away']['scratches'] = [player['lastName']['default'] for player in away_scratches]

        return data

    def get_goal_data(self):
        data = {}
        data['home'] = {}
        data['away'] = {}

        schedule_game = json.loads(self.db.get('schedule_game'))
        game_id = schedule_game['id']
        boxscore = json.loads(self.db.get('boxscore'))

        try:
            data['home']['name'] = boxscore['homeTeam']['abbrev']
            data['away']['name'] = boxscore['awayTeam']['abbrev']
        except KeyError:
            self._fetch_boxscore(game_id)
        finally:
            boxscore = json.loads(self.db.get('boxscore'))
            data['home']['name'] = boxscore['homeTeam']['abbrev']
            data['away']['name'] = boxscore['awayTeam']['abbrev']

        data['home']['score'] = self.db.get('home_goals')
        data['away']['score'] = self.db.get('away_goals')
        data['time_left'] = self.db.get('time_scored')
        data['period'] = self.db.get('period_scored')

        return data

    def get_intermission_data(self):
        data = {}
        data['home'] = {}
        data['away'] = {}

        schedule_game = json.loads(self.db.get('schedule_game'))
        game_id = schedule_game['id']
        boxscore = json.loads(self.db.get('boxscore'))

        try:
            home_stats = boxscore['homeTeam']
            away_stats = boxscore['awayTeam']
            period = boxscore['periodDescriptor']['number']
        except KeyError:
            self._fetch_boxscore(game_id)
        finally:
            boxscore = json.loads(self.db.get('boxscore'))
            home_stats = boxscore['homeTeam']
            away_stats = boxscore['awayTeam']
            period = boxscore['periodDescriptor']['number']

        if boxscore['periodDescriptor']['number'] > 3:
            period = 'OT'

        data['home']['name'] = home_stats['abbrev']
        data['home']['score'] = home_stats['score']
        data['home']['sog'] = home_stats['sog']
        data['away']['name'] = away_stats['abbrev']
        data['away']['score'] = away_stats['score']
        data['away']['sog'] = away_stats['sog']
        data['period'] = period

        return data

    def get_game_end_data(self):
        data = {}
        data['home'] = {}
        data['away'] = {}

        schedule_game = json.loads(self.db.get('schedule_game'))
        game_id = schedule_game['id']
        boxscore = json.loads(self.db.get('boxscore'))

        try:
            home_stats = boxscore['homeTeam']
            away_stats = boxscore['awayTeam']
            summary = boxscore['summary']
        except KeyError:
            self._fetch_boxscore(game_id)
        finally:
            boxscore = json.loads(self.db.get('boxscore'))
            home_stats = boxscore['homeTeam']
            away_stats = boxscore['awayTeam']

        data['home']['name'] = home_stats['abbrev']
        data['home']['score'] = home_stats['score']
        data['away']['name'] = away_stats['abbrev']
        data['away']['score'] = away_stats['score']

        for stat in summary['teamGameStats']:
            category = stat['category']
            data['home'][category] = stat['homeValue']
            data['away'][category] = stat['awayValue']

        return data

    def _fetch_schedule(self):
        today = str(date.today())

        try:
            schedule = self.client.schedule.get_schedule_by_team_by_week(team_abbr = 'TBL')
        except:
            return

        self.db.set('schedule', json.dumps(schedule))
        self.db.set('schedule_fetched', today)

    def _fetch_standings(self):
        try:
            standings = self.client.standings.get_standings()['standings']
        except:
            return

        self.db.set('standings', json.dumps(standings))

    def _fetch_boxscore(self, game_id):
        try:
            boxscore = self.client.game_center.boxscore(game_id = game_id)
        except:
            return

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
