from disnake.ext import commands
from .country_leaderboard import CountryLeaderboard
from .leaderboard_loop import LeaderboardLoop
from .server_leaderboard import ServerLeaderboard


class Leaderboards(CountryLeaderboard, LeaderboardLoop, ServerLeaderboard, commands.Cog):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot

def setup(bot):
    bot.add_cog(Leaderboards(bot))