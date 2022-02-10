import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

from helper import addLegendsPlayer_GLOBAL,getPlayer



class Check_Slash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_slash(name="check", description="Check a player's legends stats.",
                       options=[
                           create_option(
                               name="search",
                               description="Search by tag, name, or @discorduser",
                               option_type=3,
                               required=False,
                           ) ]
                       )
    async def check_tag_or_name(self, ctx,search=None):
        if search == None:
            search = str(ctx.author.id)
        embed = discord.Embed(
            description="<a:loading:884400064313819146> Fetching Stats. | Searches of 10+ players can take a few seconds, refine your search or use playertag if needed.",
            color=discord.Color.green())
        msg = await ctx.send(embed=embed)
        await self.legends(ctx, msg, search)


    async def legends(self, ctx, msg, search_query):

        search = self.bot.get_cog("search")
        results = await search.search_results(ctx, search_query)

        #track for them if not found
        if results == []:
            player = await getPlayer(search_query)
            if player is not None:

                if str(player.league) != "Legend League":
                    embed = discord.Embed(
                        description=f"{player.name} is not tracked nor is in legends.",
                        color=discord.Color.red())
                    return await msg.edit(content=None, embed=embed)

                clan_name = "No Clan"
                if player.clan != None:
                    clan_name = player.clan.name
                await addLegendsPlayer_GLOBAL(player=player, clan_name=clan_name)
                embed = discord.Embed(
                    description=f"{player.name} now tracked. View stats with `/check {player.tag}`.\n**Note:** Legends stats aren't given, so they have to be collected as they happen. Stats will appear from now & forward :)",
                    color=discord.Color.green())
                return await msg.edit(content=None,embed=embed)
            else:
                embed = discord.Embed(
                    description="**No results found.** \nCommands:\n`/track add #playerTag` to track an account.",
                    color=discord.Color.red())
                return await msg.edit(content=None, embed=embed)

        pagination = self.bot.get_cog("pagination")
        await pagination.button_pagination(ctx, msg, results)



def setup(bot):
    bot.add_cog(Check_Slash(bot))
