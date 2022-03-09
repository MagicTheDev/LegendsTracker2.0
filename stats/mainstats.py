from disnake.ext import commands
from .stats import LegendStats
from .top import Top

class MainStats(LegendStats, Top,  commands.Cog):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot

def setup(bot):
    bot.add_cog(MainStats(bot))