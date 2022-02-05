import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

from helper import addLegendsPlayer_GLOBAL, addLegendsPlayer_SERVER,getPlayer



class Check_Slash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_subcommand(base="check", name="search", description="Check a player's legends stats.",
                       options=[
                           create_option(
                               name="search",
                               description="Search by tag or name",
                               option_type=3,
                               required=True,
                           ) ]
                       )
    async def check_tag_or_name(self, ctx,search):
        embed = discord.Embed(
            description="<a:loading:884400064313819146> Fetching Stats. | Searches of 10+ players can take a few seconds, refine your search or use playertag if needed.",
            color=discord.Color.green())
        msg = await ctx.send(embed=embed)
        await self.legends(ctx, msg, search)

    @cog_ext.cog_subcommand(base="check", name="member",
                       description="Check a player's legends stats.",
                       options=[
                           create_option(
                               name="member",
                               description="Check a discord member.",
                               option_type=6,
                               required=False,
                           )]
                       )
    async def check_member(self, ctx, member=None):
        if member == None:
            member = str(ctx.author)
        else:
            member = member.id
        embed = discord.Embed(
            description="<a:loading:884400064313819146> Fetching Stats. | Searches of 10+ players can take a few seconds, refine your search or use playertag if needed.",
            color=discord.Color.green())
        msg = await ctx.send(embed=embed)

        await self.legends(ctx, msg, member)

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
                    return await ctx.edit(content=None, embed=embed)

                clan_name = "No Clan"
                if player.clan != None:
                    clan_name = player.clan.name
                await addLegendsPlayer_GLOBAL(player=player, clan_name=clan_name)
                await addLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)
                embed = discord.Embed(
                    description=f"{player.name} now tracked. View stats with `/check search {player.tag}`.\n**Note:** Legends stats aren't given, so they have to be collected as they happen. Stats will appear from now & forward :)",
                    color=discord.Color.green())
                return await ctx.edit(content=None,embed=embed)
            else:
                embed = discord.Embed(
                    description="**No results found.** \nCommands:\n`/track #playerTag` to track an account.",
                    color=discord.Color.red())
                return await ctx.edit(content=None, embed=embed)

        pagination = self.bot.get_cog("pagination")
        await pagination.button_pagination(ctx, msg, results)



def setup(bot):
    bot.add_cog(Check_Slash(bot))
