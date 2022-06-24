from disnake.ext import commands
from .stats import LegendStats

class MainStats(LegendStats, commands.Cog):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot

def setup(bot):
    bot.add_cog(MainStats(bot))
