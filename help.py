
from discord.ext import commands
import discord
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, wait_for_component
from discord_slash import cog_ext


import inspect

class help(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_slash(name='invite',
                       description="Invite for bot.")
    async def invite(self, ctx):
        await ctx.send("https://discord.com/api/oauth2/authorize?client_id=825324351016534036&permissions=2147747840&scope=bot%20applications.commands")

    @cog_ext.cog_slash(name='server',
                       description="Support server for bot.")
    async def serv(self, ctx):
        await ctx.send(
            "discord.gg/Z96S8Gg2Uv")


def setup(bot: commands.Bot):
    bot.add_cog(help(bot))