import coc
import disnake
from disnake.ext import commands
from helper import addLegendsPlayer_GLOBAL,getPlayer, ongoing_stats
SUPER_SCRIPTS=["⁰","¹","²","³","⁴","⁵","⁶", "⁷","⁸", "⁹"]
import emoji

class Check_Slash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def autocomp_names(self, user_input: str):
        search = self.bot.get_cog("search")
        results = await search.search_name(user_input)
        return results

    async def autocomp_clans(self, user_input: str):
        search = self.bot.get_cog("search")
        results = await search.search_clans(user_input)
        return results

    @commands.slash_command(name="check")
    async def check(self, ctx):
        pass


    @check.sub_command(name="search", description="Search by player tag or name to find a player")
    async def check_search(self, ctx: disnake.ApplicationCommandInteraction,
                           smart_search: str = commands.Param(autocomplete=autocomp_names)):
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

    @check.sub_command(name="user",
                            description="Check a discord user's linked accounts (empty for your own)")
    async def check_user(self, ctx: disnake.ApplicationCommandInteraction, discord_user: disnake.Member = None):
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


    @commands.slash_command(name="clan", description="Search by name or tag to find a clan.",guild_ids=[923764211845312533])
    async def check_clan(self, ctx: disnake.ApplicationCommandInteraction,
                           smart_search: str = commands.Param(autocomplete=autocomp_clans)):
        await ctx.response.defer()
        """
            Parameters
            ----------
            smart_search: Autocompletes clans using clans tracked members are in
        """
        search = self.bot.get_cog("search")
        results:coc.Clan = await search.search_clan_tag(smart_search)

        if results == None:
            embed = disnake.Embed(
                description=f"Not a valid clan tag.",
                color=disnake.Color.red())
            return await ctx.edit_original_message(content=None, embed=embed)

        ranking =[]
        num_not = 0
        for member in results.members:
            person = await ongoing_stats.find_one({'tag': member.tag})
            if person is None:
                if str(member.league) == "Legend League":
                    num_not += 1
                continue

            league = person.get("league")
            if league != "Legend League":
                continue

            thisPlayer = []
            trophy = person.get("trophies")

            name = person.get("name")
            name = emoji.get_emoji_regexp().sub('', name)
            name = f"{name}"
            hits = person.get("today_hits")
            hits = sum(hits)
            numHit = person.get("num_today_hits")
            defs = person.get("today_defenses")
            numDef = len(defs)
            defs = sum(defs)

            started = trophy - (hits - defs)

            thisPlayer.append(name)
            thisPlayer.append(started)
            thisPlayer.append(hits)
            thisPlayer.append(numHit)
            thisPlayer.append(defs)
            thisPlayer.append(numDef)
            thisPlayer.append(trophy)

            ranking.append(thisPlayer)

        ranking = sorted(ranking, key=lambda l: l[6], reverse=True)

        text = ""
        initial = f"__**{results.name} Legends Check**__\n"
        embeds = []
        x = 0
        for player in ranking:
            name = player[0]
            hits = player[2]
            hits = player[2]
            numHits = player[3]
            if numHits >= 9:
                numHits = 8
            defs = player[4]
            numDefs = player[5]
            numHits = SUPER_SCRIPTS[numHits]
            numDefs = SUPER_SCRIPTS[numDefs]
            trophies = player[6]
            text += f"\u200e**<:trophyy:849144172698402817>{trophies} | \u200e{name}**\n➼ <a:swords:944894455633297418> {hits}{numHits} <:clash:877681427129458739> {defs}{numDefs}\n"
            x += 1
            if x == 25:
                embed = disnake.Embed(title=f"__**{results.name} Legends Check**__",
                                      description=text)
                embed.set_thumbnail(url=results.badge.large)
                if num_not != 0:
                    embed.set_footer(text=f"{num_not} players untracked.")
                x = 0
                embeds.append(embed)
                text = ""

        if text != "":
            embed = disnake.Embed(title=f"__**{results.name} Legends Check**__",
                                  description=text)
            embed.set_thumbnail(url=results.badge.large)
            if num_not != 0:
                embed.set_footer(text=f"{num_not} players untracked.")
            embeds.append(embed)

        options = []
        if len(embeds) == 2:
            options.append(disnake.SelectOption(label="Page 1 (1-25)", value=f"0", emoji="📄"))
            options.append(disnake.SelectOption(label="Page 2 (25-50)", value=f"1", emoji="📄"))

        if num_not != 0:
            options.append(disnake.SelectOption(label="Track Missing Players", value=f"{results.tag}", emoji="🔀"))

        if options == []:
            return await ctx.edit_original_message(embed=embeds[0])

        select1 = disnake.ui.Select(
            options=options,
            placeholder="Page Navigation",
            min_values=1,  # the minimum number of options a user must select
            max_values=1  # the maximum number of options a user can select
        )
        action_row = disnake.ui.ActionRow()
        action_row.append_item(select1)

        current_page = 0
        await ctx.edit_original_message(embed=embeds[0], components=[action_row])
        msg = await ctx.original_message()

        def check(res: disnake.MessageInteraction):
            return res.message.id == msg.id

        while True:
            try:
                res: disnake.MessageInteraction = await self.bot.wait_for("message_interaction", check=check,
                                                                          timeout=600)
            except:
                await msg.edit(components=[])
                break

            if res.author.id != ctx.author.id:
                await res.send(content="You must run the command yourself to interact with components.", ephemeral=True)
                continue

            # print(res.custom_id)
            if res.values[0] == "0" or res.values[0] == "1":
                current_page = int(res.values[0])
                await res.response.edit_message(embed=embeds[current_page],
                                                components=[action_row])

            else:
                embed = disnake.Embed(
                    description="<a:loading:884400064313819146> Adding players...",
                    color=disnake.Color.green())
                await res.send(embed=embed, ephemeral=True)

                num_global_tracked = 0
                async for player in results.get_detailed_members():
                    if str(player.league) == "Legend League":
                        is_global_tracked = await self.check_global_tracked(player=player)
                        if not is_global_tracked:
                            num_global_tracked += 1
                            await addLegendsPlayer_GLOBAL(player=player, clan_name=results.name)


                embed = disnake.Embed(
                    title=f"{results.name}",
                    description=f"{num_global_tracked} members added to global tracking.",
                    color=disnake.Color.green())
                embed.set_thumbnail(url=results.badge.large)
                og = await res.original_message()
                return await og.edit(embed=embed)


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

    async def check_global_tracked(self,player):
        results = await ongoing_stats.find_one({"tag": f"{player.tag}"})
        return results != None


def setup(bot):
    bot.add_cog(Check_Slash(bot))
