from disnake.ext import commands
from .clan_track import ClanTrack
from .player_track import PlayerTrack


class Track(ClanTrack, PlayerTrack, commands.Cog):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot

def setup(bot):
    bot.add_cog(Track(bot))