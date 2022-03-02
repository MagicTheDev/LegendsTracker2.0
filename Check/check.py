import disnake
from disnake.ext import commands
from helper import addLegendsPlayer_GLOBAL,getPlayer


class Check_Slash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def autocomp_names(self, user_input: str):
        search = self.bot.get_cog("search")
        results = await search.search_name(user_input)
        return results


    @commands.slash_command(name="check_search", description="Search by player tag or name to find a player")
    async def check_search(self, ctx: disnake.ApplicationCommandInteraction , smart_search: str = commands.Param(autocomplete=autocomp_names)):
        """
            Parameters
            ----------
            smart_search: Type a search, pick an option, or don't to get multiple results back
        """
        if smart_search == None:
            smart_search = str(ctx.author.id)

        embed = disnake.Embed(
            description="<a:loading:884400064313819146> Fetching Stats. | Searches of 10+ players can take a few seconds, refine your search or use playertag if needed.",
            color=disnake.Color.green())
        await ctx.send(embed=embed)
        msg = await ctx.original_message()
        await self.legends(ctx, msg, smart_search)


    @commands.slash_command(name="check_user", description="Check a discord user's linked accounts (empty for your own)")
    async def check_user(self, ctx: disnake.ApplicationCommandInteraction, discord_user: disnake.Member=None):
        """
            Parameters
            ----------
            discord_user: Search by @discordUser
        """
        if discord_user == None:
            discord_user = str(ctx.author.id)
        else:
            discord_user = str(discord_user.id)

        embed = disnake.Embed(
            description="<a:loading:884400064313819146> Fetching Stats. | Searches of 10+ players can take a few seconds, refine your search or use playertag if needed.",
            color=disnake.Color.green())
        await ctx.send(embed=embed)
        msg = await ctx.original_message()
        await self.legends(ctx, msg, discord_user)


    async def legends(self, ctx, msg, search_query):

        search = self.bot.get_cog("search")
        results = await search.search_results(ctx, search_query)

        #track for them if not found
        if results == []:
            player = await getPlayer(search_query)
            if player is not None:

                if str(player.league) != "Legend League":
                    embed = disnake.Embed(
                        description=f"{player.name} is not tracked nor is in legends.",
                        color=disnake.Color.red())
                    return await msg.edit(content=None, embed=embed)

                clan_name = "No Clan"
                if player.clan != None:
                    clan_name = player.clan.name
                await addLegendsPlayer_GLOBAL(player=player, clan_name=clan_name)
                embed = disnake.Embed(
                    description=f"{player.name} now tracked. View stats with `/check {player.tag}`.\n**Note:** Legends stats aren't given, so they have to be collected as they happen. Stats will appear from now & forward :)",
                    color=disnake.Color.green())
                return await msg.edit(content=None,embed=embed)
            else:
                embed = disnake.Embed(
                    description="**No results found.** \nCommands:\n`/track add #playerTag` to track an account.",
                    color=disnake.Color.red())
                return await msg.edit(content=None, embed=embed)

        pagination = self.bot.get_cog("pagination")
        await pagination.button_pagination(ctx, msg, results)



def setup(bot):
    bot.add_cog(Check_Slash(bot))
