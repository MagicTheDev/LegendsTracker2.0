import discord
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands
from discord.ext.commands.context import Context

from helper import addLegendsPlayer_GLOBAL, addLegendsPlayer_SERVER,getPlayer
from helper import server_db


class Check_Slash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # <discord.commands.commands.SlashCommandGroup>
        check = SlashCommandGroup(name ="check",
                                  description="Commands to check a player's legends stats.",
                                  guild_ids=[328997757048324101, 923764211845312533])

        @check.command(name="search",description="Check a player's legends stats.")
        async def check_tag_or_name(
            ctx: Context,
            search : Option(str, description="Search by tag or name", required=True),
        ):
            embed = discord.Embed(
                description="<a:loading:884400064313819146> Fetching Stats. | Searches of 10+ players can take a few seconds, refine your search or use playertag if needed.",
                color=discord.Color.green())
            await ctx.respond(embed=embed)
            await legends(ctx, search)

        @check.command(name="member",description="Check a player's legends stats.")
        async def check_member(
            ctx: Context,
            member: Option(discord.Member, required=False) = None,
        ):
            if member == None:
                member = str(ctx.author)
            else:
                member = member.id
            embed = discord.Embed(
                description="<a:loading:884400064313819146> Fetching Stats. | Searches of 10+ players can take a few seconds, refine your search or use playertag if needed.",
                color=discord.Color.green())
            msg = await ctx.respond(embed=embed)

            await legends(ctx, msg, member)

        async def legends(ctx, search_query):

            search = bot.get_cog("search")
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
            await pagination.button_pagination(ctx, results)


        # Adds the application command
        bot.add_application_command(check)


def setup(bot):
    bot.add_cog(Check_Slash(bot))
