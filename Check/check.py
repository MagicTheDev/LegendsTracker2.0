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
        results = await search.search_clan_tag(smart_search)

        if results == []:
            embed = disnake.Embed(
                description=f"Not a valid clan tag.",
                color=disnake.Color.red())
            return await ctx.edit_original_message(content=None, embed=embed)

        results = results[0]
        print(results)
        ranking =[]
        for member in results.members:
            person = await ongoing_stats.find_one({'tag': member.tag})
            if person is None:
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
            text += f"\u200e**<:trophyy:849144172698402817>\u200e{trophies} | \u200e{name}**\n➼ <:sword_coc:940713893926428782> {hits}{numHits} <:clash:877681427129458739> {defs}{numDefs}\n"
            x += 1
            if x == 25:
                embed = disnake.Embed(title=f"__**{results.name} Legends Check**__",
                                      description=text)
                embed.set_thumbnail(url=results.badge.large)
                x = 0
                embeds.append(embed)
                text = ""

        if text != "":
            embed = disnake.Embed(title=f"__**{results.name} Legends Check**__",
                                  description=text)
            embed.set_thumbnail(url=results.badge.large)
            embeds.append(embed)

        current_page = 0
        await ctx.edit_original_message(embed=embeds[0], components=self.create_components(current_page, embeds))
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
            if res.data.custom_id == "Previous":
                current_page -= 1
                await res.response.edit_message(embed=embeds[current_page],
                                                components=self.create_components(current_page, embeds))

            elif res.data.custom_id == "Next":
                current_page += 1
                await res.response.edit_message(embed=embeds[current_page],
                                                components=self.create_components(current_page, embeds))


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


    def create_components(self, current_page, embeds):
        length = len(embeds)
        if length == 1:
            return []

        page_buttons = [
            disnake.ui.Button(label="", emoji="◀️", style=disnake.ButtonStyle.blurple, disabled=(current_page == 0),
                              custom_id="Previous"),
            disnake.ui.Button(label=f"Page {current_page + 1}/{length}", style=disnake.ButtonStyle.grey,
                              disabled=True),
            disnake.ui.Button(label="", emoji="▶️", style=disnake.ButtonStyle.blurple,
                              disabled=(current_page == length - 1), custom_id="Next")
        ]
        buttons = disnake.ui.ActionRow()
        for button in page_buttons:
            buttons.append_item(button)

        return [buttons]

def setup(bot):
    bot.add_cog(Check_Slash(bot))
