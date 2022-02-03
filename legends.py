

from clashClient import getPlayer

import motor.motor_asyncio
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")


class legends(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_slash(name="legends",
                       description="Legends stats . Choose a stat type, if no search type chosen, defaults to own accounts.",
                       options=[
                           create_option(
                               name="search",
                               description="[OPTIONAL] Search, this can be by name (i.e Mike) or PlayerTag",
                               option_type=3,
                               required=False,
                           ),
                           create_option(
                               name="user",
                               description="[OPTIONAL] Lookup/Check a User.",
                               option_type=6,
                               required=False,
                           )
                       ]
                       )
    async def slash_legends(self, ctx, user=None, search=None):
        await ctx.defer()
        search_query = None
        if search != search_query:
            search_query = str(search)
        elif user != search_query:
            search_query = str(user.id)
        else:
            search_query = str(ctx.author.id)
        embed = discord.Embed(
            description="<a:loading:884400064313819146> Fetching Stats.",
            color=discord.Color.green())
        msg = await ctx.reply(embed=embed)
        await self.legends(ctx, msg,search_query)


    @commands.command(name="checks", aliases=["check", "graph"])
    async def prefix_legends(self,ctx, *, search_query = None):
        if search_query == None:
            search_query = str(ctx.message.author.id)
        embed = discord.Embed(
            description="<a:loading:884400064313819146> Fetching Stats. | Searches of 10+ players can take a few seconds, refine your search or use playertag if needed.",
            color=discord.Color.green())
        msg = await ctx.reply(embed=embed, mention_author = False)
        await self.legends(ctx, msg, search_query)





def setup(bot: commands.Bot):
    bot.add_cog(legends(bot))