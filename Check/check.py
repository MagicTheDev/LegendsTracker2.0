import discord
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands
from discord.ext.commands.context import Context

from helper import addLegendsPlayer, getPlayer
from helper import server_db




class Check_Slash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # <discord.commands.commands.SlashCommandGroup>
        check = SlashCommandGroup(name ="check",
                                  description="Commands to check a player's legends stats.",
                                  guild_ids=[328997757048324101])

        @check.command(name="search",description="Check a player's legends stats.")
        async def check_tag_or_name(
            ctx: Context,
            search : Option(str, description="Search by tag or name", required=True),
        ):
            embed = discord.Embed(
                description="<a:loading:884400064313819146> Fetching Stats. | Searches of 10+ players can take a few seconds, refine your search or use playertag if needed.",
                color=discord.Color.green())
            msg = await ctx.reply(embed=embed, mention_author=False)
            await legends(ctx, msg, search)

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

        async def legends(ctx, msg, search_query):

            search = bot.get_cog("search")
            results = await search.search_results(ctx, search_query)
            # print(results)

            if results == []:
                player = await getPlayer(search_query)
                if player is not None:

                    if str(player.league) != "Legend League":
                        embed = discord.Embed(
                            description=f"{player.name} is not tracked and is not in legends.",
                            color=discord.Color.red())
                        return await msg.edit(content=None, embed=embed)

                    embed = discord.Embed(
                        description=f"{player.name} is not tracked. Would you like to track them?",
                        color=discord.Color.red())
                    page_buttons = [
                        create_button(label="Yes", style=ButtonStyle.green,
                                      custom_id="Yes"),
                        create_button(label="No", style=ButtonStyle.red, custom_id="No")]
                    page_buttons = create_actionrow(*page_buttons)
                    await msg.edit(content=None, embed=embed, components=[page_buttons])

                    while True:

                        try:
                            res = await wait_for_component(self.bot,
                                                           components=page_buttons,
                                                           messages=msg, timeout=600)
                        except:
                            await msg.edit(components=[])
                            break

                        if res.author_id != ctx.author.id:
                            await res.send(content="You must run the command to interact with components.", hidden=True)
                            continue

                        if res.custom_id == "Yes":
                            clan_name = "No Clan"
                            if player.clan != None:
                                clan_name = player.clan.name
                            await addLegendsPlayer(player=player, clan_name=clan_name)
                            embed = discord.Embed(
                                description=f"{player.name} now tracked. View stats with `do check {player.tag}`.\nNote: Legends stats aren't given, so they have to be collected as they happen. Stats will appear from now & forward :)",
                                color=discord.Color.green())
                            return await msg.edit(embed=embed,
                                                  components=[])


                        elif res.custom_id == "No":
                            embed = discord.Embed(
                                description=f"Sounds good. Track them in the future with `do track {player.tag}`.",
                                color=discord.Color.green())
                            return await msg.edit(embed=embed,
                                                  components=[])
                else:
                    embed = discord.Embed(
                        description="**No results found.** \nCommands:\n`do track #playerTag` to track an account \n`do feed #playerTag` to add account to server legends feed\n`do help` to see all commands.",
                        color=discord.Color.red())
                    return await msg.edit(content=None, embed=embed)

            pagination = self.bot.get_cog("pagination")
            await pagination.button_pagination(ctx, msg, results)




        # Adds the application command
        bot.add_application_command(check)


def setup(bot):
    bot.add_cog(Check_Slash(bot))
