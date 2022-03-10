from disnake.ext import commands
from .country_leaderboard import CountryLeaderboard
from .server_leaderboard import ServerLeaderboard


class Leaderboards(CountryLeaderboard, ServerLeaderboard, commands.Cog):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot

def setup(bot):
    bot.add_cog(Leaderboards(bot))