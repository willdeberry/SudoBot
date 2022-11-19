
import discord
from discord import app_commands

from utilities.helpers import build_embed
from sports.football_game import FootballGame


class BucsCommands(app_commands.Group):
    _base_url = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'bucs'
        self.football_game = FootballGame()

    @app_commands.command(description = 'Next scheduled game')
    async def next(self, ctx):
        details = self.football_game.bucs_next_game()

        if not details:
            await ctx.response.send_message('Bye Week')
            return

        fields = [
            {'name': 'Date', 'value': f"{details['time']} @ {details['venue']}"},
            {'name': 'Matchup', 'value': details['matchup']},
            {'name': 'Broadcasts', 'value': details['broadcasts'], 'inline': True},
            {'name': 'Streams', 'value': details['streams'], 'inline': True}
        ]
        embed = build_embed('Next Game', fields)

        await ctx.response.send_message(embed = embed)

    @app_commands.command(description = 'Current record')
    async def record(self, ctx):
        details = self.football_game.bucs_record()
        fields = [
            {'name': 'Games Played', 'value': details['games_played'], 'inline': True},
            {'name': 'Record', 'value': details['record'], 'inline': True}
        ]
        embed = build_embed("Buc's Record", fields)

        await ctx.response.send_message(embed = embed)
