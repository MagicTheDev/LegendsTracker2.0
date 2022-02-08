
from discord.ext import commands
import discord
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, wait_for_component
from discord_slash import cog_ext




import inspect

class help(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="check")
    async def check(self, ctx):
        await ctx.send("All commands have been moved to slash commands. Start with a `/` in the chat to view them.\n"
                       "Slash commands not showing up? Reinvite me.\nNeed Help? Join the support server - discord.gg/Z96S8Gg2Uv\nhttps://discord.com/api/oauth2/authorize?client_id=825324351016534036&permissions=2147747840&scope=bot%20applications.commands")

    @commands.command(name='leave')
    @commands.is_owner()
    async def leaveg(self, ctx, *, guild_name):
        guild = discord.utils.get(self.bot.guilds, name=guild_name)  # Get the guild by name
        if guild is None:
            await ctx.send("No guild with that name found.")  # No guild found
            return
        await guild.leave()  # Guild found
        await ctx.send(f"I left: {guild.name}!")


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