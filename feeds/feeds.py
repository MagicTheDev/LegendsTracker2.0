from disnake.ext import commands
from .dm_feed import DMFeed
from .feed_buttons import FeedButtons
from .legend_feed import LegendsFeed


class Feeds(DMFeed, FeedButtons, LegendsFeed, commands.Cog):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot

def setup(bot):
    bot.add_cog(Feeds(bot))