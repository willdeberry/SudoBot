
import requests


class Status:
    _base_url = 'https://api.uptimerobot.com/v2'
    _statuses = {
        0: 'Paused',
        1: 'Not checked yet',
        2: 'Up',
        8: 'Seems down',
        9: 'Down'
    }

    def __init__(self, api_key):
        self.api_key = api_key

    def _fetch_monitors(self):
        payload = requests.post(f'{self._base_url}/getMonitors?format=json&api_key={self.api_key}').json()
        return payload['monitors']

    def _create_fields(self, monitor):
        return {"name": monitor['friendly_name'], "value": self._statuses[monitor['status']]}

    def get_current(self):
        fields = []

        monitors = self._fetch_monitors()

        for monitor in monitors:
            field = self._create_fields(monitor)
            fields.append(field)

        return fields
