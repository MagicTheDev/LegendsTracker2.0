import coc
import disnake
from disnake.ext import commands
from utils.helper import getPlayer, ongoing_stats, translate, has_single_plan, has_guild_plan, decrement_usage, coc_client
from utils.db import addLegendsPlayer_GLOBAL
from utils.components import leaderboard_components
from utils.search import search_clans_with_tag, search_clan_tag, search_results, search_name_with_tag
SUPER_SCRIPTS=["⁰","¹","²","³","⁴","⁵","⁶", "⁷","⁸", "⁹"]
import emoji
from coc import utils

class Check(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def autocomp_names(self, user_input: str):
        results = await search_name_with_tag(user_input)
        return results

    async def autocomp_clans(self, user_input: str):
        results = await search_clans_with_tag(user_input)
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
        SINGLE_PLAN = await has_single_plan(ctx)
        GUILD_PLAN = await has_guild_plan(ctx)
        TIER, NUM_COMMANDS, MESSAGE = await decrement_usage(ctx, SINGLE_PLAN, GUILD_PLAN)
        if MESSAGE is not None:
            await ctx.response.defer(ephemeral=True)
            return await ctx.send(content=MESSAGE)

        await ctx.response.defer()

        if "|" in smart_search and "#" in smart_search:
            search = smart_search.split("|")
            tag = search[-1]
        else:
            tag = smart_search

        embed = disnake.Embed(
            description=translate("check_loading", ctx),
            color=disnake.Color.green())
        await ctx.edit_original_message(embed=embed)
        msg = await ctx.original_message()
        await self.legends(ctx, msg, tag, True)

    @check.sub_command(name="user",
                            description="Check a discord user's linked accounts (empty for your own)")
    async def check_user(self, ctx: disnake.ApplicationCommandInteraction, discord_user: disnake.Member = None):
        """
            Parameters
            ----------
            discord_user: Search by @discordUser
        """
        SINGLE_PLAN = await has_single_plan(ctx)
        GUILD_PLAN = await has_guild_plan(ctx)
        TIER, NUM_COMMANDS, MESSAGE = await decrement_usage(ctx, SINGLE_PLAN, GUILD_PLAN)
        if MESSAGE is not None:
            await ctx.response.defer(ephemeral=True)
            return await ctx.send(content=MESSAGE)

        if discord_user is None:
            discord_user = str(ctx.author.id)
        else:
            discord_user = str(discord_user.id)

        embed = disnake.Embed(
            description=translate("check_loading", ctx),
            color=disnake.Color.green())
        await ctx.send(embed=embed)
        msg = await ctx.original_message()
        await self.legends(ctx, msg, discord_user, False)


    @check.sub_command(name="clan", description="Search by name or tag to find a clan.")
    async def check_clan(self, ctx: disnake.ApplicationCommandInteraction,
                           smart_search: str = commands.Param(autocomplete=autocomp_clans)):
        """
            Parameters
            ----------
            smart_search: Autocompletes clans using clans tracked members are in
        """
        SINGLE_PLAN = await has_single_plan(ctx)
        GUILD_PLAN = await has_guild_plan(ctx)
        TIER, NUM_COMMANDS, MESSAGE = await decrement_usage(ctx, SINGLE_PLAN, GUILD_PLAN)
        if MESSAGE is not None:
            await ctx.response.defer(ephemeral=True)
            return await ctx.send(content=MESSAGE)

        await ctx.response.defer()
        if "|" in smart_search and "#" in smart_search:
            search = smart_search.split("|")
            tag = search[-1]
        else:
            tag = smart_search

        results:coc.Clan = await search_clan_tag(tag)

        if results is None or results.member_count == 0:
            embed = disnake.Embed(
                description=translate("not_valid_clan_tag", ctx),
                color=disnake.Color.red())
            return await ctx.edit_original_message(content=None, embed=embed)

        ranking =[]
        num_not = 0
        for member in results.members:
            person = await ongoing_stats.find_one({'tag': member.tag})
            if person is None:
                if str(member.league) == "Legend League" and member.trophies >= 5000:
                    await addLegendsPlayer_GLOBAL(member, results.name, True)
                    person = await ongoing_stats.find_one({'tag': member.tag})
                else:
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

        if len(ranking) == 0:
            embed = disnake.Embed(
                description=translate("no_legend_players", ctx),
                color=disnake.Color.red())
            return await ctx.edit_original_message(content=None, embed=embed)

        ranking = sorted(ranking, key=lambda l: l[6], reverse=True)

        ALPHABET = 0; STARTED = 1; OFFENSE = 2; DEFENSE = 4; TROPHIES = 6
        sort_types = {0: "Alphabetically", 1: "by Start Trophies", 2: "by Offense", 4: "by Defense", 6: "by Current Trophies"}
        sort_type = 6
        embeds = await self.create_embed(ctx, ranking, results)
        embed = embeds[0]
        embed.set_footer(text=f"Sorted {sort_types[sort_type]}")
        current_page = 0
        await ctx.edit_original_message(embed=embed,
                                        components=leaderboard_components(self.bot, current_page, embeds, ctx))
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

            if res.data.component_type.value == 2:
                if res.data.custom_id == "Previous":
                    current_page -= 1
                    embed = embeds[current_page]
                    embed.set_footer(text=f"{translate('sorted', ctx)} {translate(sort_types[sort_type], ctx)}")
                    await res.response.edit_message(embed=embed,
                                                    components=leaderboard_components(self.bot, current_page, embeds,
                                                                                      ctx))

                elif res.data.custom_id == "Next":
                    current_page += 1
                    embed = embeds[current_page]
                    embed.set_footer(text=f"{translate('sorted', ctx)} {translate(sort_types[sort_type], ctx)}")
                    await res.response.edit_message(embed=embed,
                                                    components=leaderboard_components(self.bot, current_page, embeds,
                                                                                      ctx))
            else:
                current_page = 0
                sort_type = int(res.values[0])
                ranking = sorted(ranking, key=lambda l: l[int(res.values[0])],
                                 reverse=int(res.values[0]) != 0 and int(res.values[0]) != 4)
                embeds = await self.create_embed(ctx, ranking, results)
                embed = embeds[current_page]
                embed.set_footer(text=f"{translate('sorted', ctx)} {translate(sort_types[sort_type], ctx)}")
                await res.response.edit_message(embed=embed,
                                                components=leaderboard_components(self.bot, current_page, embeds, ctx))


    async def legends(self, ctx, msg, search_query, ez_look):
        results = await search_results(ctx, search_query)

        if results == []:
            if utils.is_valid_tag(search_query[:-1]):
                results = await search_results(ctx, search_query[:-1])

        #track for them if not found
        if results == []:
            player = await getPlayer(search_query)
            if player is not None:
                if str(player.league) != "Legend League":
                    embed = disnake.Embed(
                        description=translate("not_tracked_nor_legends",ctx).format(player_name=player.name),
                        color=disnake.Color.red())
                    return await msg.edit(content=None, embed=embed)

                clan_name = translate("no_clan", ctx)
                if player.clan is not None:
                    clan_name = player.clan.name
                await addLegendsPlayer_GLOBAL(player=player, clan_name=clan_name)
                embed = disnake.Embed(
                    description=translate("now_tracked",ctx).format(player_name=player.name, player_tag=player.tag),
                    color=disnake.Color.green())
                return await msg.edit(content=None,embed=embed)
            else:
                embed = disnake.Embed(
                    description=translate("no_results", ctx),
                    color=disnake.Color.red())
                return await msg.edit(content=None, embed=embed)

        pagination = self.bot.get_cog("MainCheck")
        await pagination.button_pagination(msg, results, ez_look, ctx)

    async def check_global_tracked(self,player):
        results = await ongoing_stats.find_one({"tag": f"{player.tag}"})
        return results is not None


    async def create_embed(self, ctx, ranking, results):
        text = ""
        embeds = []
        x = 0
        for player in ranking:
            name = player[0]
            hits = player[2]
            numHits = player[3]
            if numHits >= 9:
                numHits = 8
            defs = player[4]
            numDefs = player[5]
            numHits = SUPER_SCRIPTS[numHits]
            numDefs = SUPER_SCRIPTS[numDefs]
            trophies = player[6]
            text += f"\u200e**<:trophyy:849144172698402817>{trophies} | \u200e{name}**\n➼ <:cw:948845649229647952> {hits}{numHits} <:sh:948845842809360424> {defs}{numDefs}\n"
            x += 1
            if x == 25:
                embed = disnake.Embed(title=f"__**{results.name}**__",
                                      description=text)
                embed.set_thumbnail(url=results.badge.large)
                x = 0
                embeds.append(embed)
                text = ""

        if text != "":
            embed = disnake.Embed(title=f"__**{results.name}**__",
                                  description=text)
            embed.set_thumbnail(url=results.badge.large)
            embeds.append(embed)

        if len(embeds) == 0:
            embed = disnake.Embed(title=f"__**{results.name}**__",
                                  description=translate("no_players_tracked", ctx))
            embed.set_thumbnail(url=results.badge.large)
            embeds.append(embed)

        return embeds