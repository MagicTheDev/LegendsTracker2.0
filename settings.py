from discord.ext import commands
import discord


class bot_settings(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.command(name='servers')
    @commands.is_owner()
    async def servers(self, ctx):
        text = ""
        guilds = self.bot.guilds
        for guild in guilds:
            id =guild.member_count
            #owner = await self.bot.fetch_user(id)
            text += guild.name +f" | {id} members\n"

        embed = discord.Embed(description=text,
                              color=discord.Color.green())


        await ctx.send(embed =embed)






def setup(bot: commands.Bot):
    bot.add_cog(bot_settings(bot))