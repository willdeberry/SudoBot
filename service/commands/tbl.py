
import discord
from discord import app_commands

from utilities.helpers import build_embed
from sports.hockey_game import HockeyGame


class TBLCommands(app_commands.Group):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'tbl'
        self.hockey_game = HockeyGame()

    @app_commands.command(description = 'Next scheduled game')
    async def next(self, ctx):
        details = self.hockey_game.tbl_next_game()
        fields = [
                {'name': 'Date', 'value': f"{details['time']} @ {details['venue']}"},
                {'name': 'Versus', 'value': details['versus']},
                {'name': 'Broadcasts', 'value': details['broadcasts'], 'inline': True},
                {'name': 'Streams', 'value': details['streams'], 'inline': True}
            ]
        embed = build_embed('Next Game', fields)

        await ctx.response.send_message(embed = embed)

    @app_commands.command(description = 'Current record')
    async def record(self, ctx):
        details = self.hockey_game.tbl_record()
        fields = [
                {'name': 'Games Played', 'value': details['games_played']},
                {'name': 'Wins', 'value': details['wins'], 'inline': True},
                {'name': 'Losses', 'value': details['losses'], 'inline': True},
                {'name': 'OT Losses', 'value': details['ot'], 'inline': True},
                {'name': 'Points', 'value': details['points']}
            ]
        embed = build_embed("TBL's Record", fields)

        await ctx.response.send_message(embed = embed)

    @app_commands.command(description = 'Current score of game if one is in progress')
    async def score(self, ctx):
        details = self.hockey_game.tbl_score()

        if not details:
            await ctx.response.send_message('No game in progress.')
            return

        home = details['home']
        away = details['away']
        fields = [{'name': 'Game', 'value': f"{home['name']} {home['score']} - {away['score']} {away['name']}"}]
        return build_message('Current Score', fields)
        await ctx.response.send_message(embed = embed)
