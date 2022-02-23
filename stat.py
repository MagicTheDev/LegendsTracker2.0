from statcord import StatcordClient
from discord.ext import commands
from helper import ongoing_stats

class MyStatcordCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.statcord_client = StatcordClient(bot, "statcord.com-rsmhOZRkiyBTI2C7z4i6", self.members_served, self.guilds_served)

    def cog_unload(self):
        self.statcord_client.close()

    async def members_served(self):
        members = await ongoing_stats.count_documents(filter={})
        return members

    async def guilds_served(self):
        members = 0
        for guild in self.bot.guilds:
            members += guild.member_count - 1
        return members

def setup(bot: commands.Bot):
    bot.add_cog(MyStatcordCog(bot))
