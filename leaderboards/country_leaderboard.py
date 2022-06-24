
from disnake.ext import commands
from utils.helper import coc_client, locations, translate, has_single_plan, has_guild_plan, decrement_usage, MissingGuildPlan
from utils.discord import partial_emoji_gen
from utils.emojis import fetch_emojis
from utils.db import *
from utils.components import create_components
SUPER_SCRIPTS=["⁰","¹","²","³","⁴","⁵","⁶", "⁷","⁸", "⁹"]
import emoji
import disnake
import re


class CountryLeaderboard(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot



    @commands.slash_command(name="country", description="test")
    async def country(self, ctx):
        pass

    @country.sub_command(name="leaderboards", description="Search country (or global) leaderboards")
    async def country_lb(self, ctx: disnake.ApplicationCommandInteraction , country: str):
        SINGLE_PLAN = await has_single_plan(ctx)
        GUILD_PLAN = await has_guild_plan(ctx)
        TIER, NUM_COMMANDS, MESSAGE = await decrement_usage(ctx, SINGLE_PLAN, GUILD_PLAN)
        if MESSAGE is not None:
            await ctx.response.defer(ephemeral=True)
            return await ctx.send(content=MESSAGE)

        await ctx.response.defer()
        loc = await coc_client.get_location_named(country)
        if country == "Global":
            embeds = await self.create_lb("global", ctx)
        else:
            if loc is None:
                return await ctx.edit_original_message(content=translate("not_valid_country", ctx))
            embeds = await self.create_lb(loc.id, ctx)

        current_page = 0
        await ctx.edit_original_message(embed=embeds[0], components=create_components(self.bot, current_page, embeds, True))
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

            if res.data.custom_id == "Previous":
                current_page -= 1
                await res.response.edit_message(embed=embeds[current_page],
                                                components=create_components(self.bot, current_page, embeds, True))

            elif res.data.custom_id == "Next":
                current_page += 1
                await res.response.edit_message(embed=embeds[current_page],
                                                components=create_components(self.bot, current_page, embeds, True))

            elif res.data.custom_id == "Print":
                await msg.delete()
                for embed in embeds:
                    await ctx.channel.send(embed=embed)


    @country.sub_command(name="track", description="Add players from country (or global) leaderboards")
    @commands.has_guild_permissions(manage_guild=True)
    async def country_track(self,ctx: disnake.ApplicationCommandInteraction, country: str, top: int = 200):
        """
            Parameters
            ----------
            country: Country to track
            top: Top # of players to track (1 - 200), default is 200
          """

        SINGLE_PLAN = await has_single_plan(ctx)
        GUILD_PLAN = await has_guild_plan(ctx)

        if GUILD_PLAN is False:
            raise MissingGuildPlan

        TIER, NUM_COMMANDS, MESSAGE = await decrement_usage(ctx, SINGLE_PLAN, GUILD_PLAN, True)
        if MESSAGE is not None:
            await ctx.response.defer(ephemeral=True)
            return await ctx.send(content=MESSAGE)

        if top <= 0 or top >= 201:
            embed = disnake.Embed(description=translate("top_number", ctx),
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)

        results = await server_db.find_one({"server": ctx.guild.id})
        tracked_members = results.get("tracked_members")
        feed = results.get("channel_id")
        if len(tracked_members) > 500 and feed is not None:
            embed = disnake.Embed(
                description=translate("500_limit", ctx),
                color=disnake.Color.red())
            return await ctx.send(embed=embed)

        await ctx.response.defer()
        if country == "Global":
            location_id = "global"
        else:
            loc = await coc_client.get_location_named(country)
            if loc is None:
                return await ctx.edit_original_message(
                    content="Not a valid country. Use the autocomplete to help select from the 100+ countries.")
            location_id = loc.id

        if country == "Global":
            country_name = "Global"
        else:
            country_name = await coc_client.get_location(location_id)

        country = await coc_client.get_location_players(location_id=location_id)

        embed = disnake.Embed(description=f"**{translate('warning_country_track1',ctx).format(top=top, country_name=country_name)}**\n"
                                          f"**{translate('warning_country_track2',ctx)}**\n"
                                          f"{translate('warning_country_track3',ctx)}\n",
                              color=disnake.Color.green())

        select1 = disnake.ui.Select(
            options=[
                disnake.SelectOption(label=translate("yes",ctx), value=f"Yes", emoji="✅"),
                disnake.SelectOption(label=translate("no",ctx), value=f"No", emoji="❌"),
                disnake.SelectOption(label=translate("cancel",ctx), emoji=partial_emoji_gen(self.bot, fetch_emojis("trashcan")),value="cancel")
            ],
            placeholder=translate("choose_option", ctx),
            min_values=1,  # the minimum number of options a user must select
            max_values=1  # the maximum number of options a user can select
        )
        action_row = disnake.ui.ActionRow()
        action_row.append_item(select1)

        await ctx.edit_original_message(embed=embed, components=[action_row])
        msg = await ctx.original_message()

        chose = False

        def check(res: disnake.MessageInteraction):
            return res.message.id == msg.id

        res = None
        while chose is False:
            try:
                res: disnake.MessageInteraction = await self.bot.wait_for("message_interaction", check=check,
                                                                          timeout=600)
            except:
                break

            if res.author.id != ctx.author.id:
                await res.send(content=translate("must_run_interact", ctx), ephemeral=True)
                continue

            chose = res.values[0]
            if chose == "cancel":
                embed = disnake.Embed(description=translate("canceling_command", ctx),
                                      color=disnake.Color.green())
                return await res.response.edit_message(embed=embed,
                                                       components=[])


        embed = disnake.Embed(
            description=f"<a:loading:884400064313819146> {translate('adding_players', ctx)}...",
            color=disnake.Color.green())
        await res.response.edit_message(embed=embed, components=[])

        num_global_tracked = 0
        num_global_alr = 0
        num_server_tracked = 0
        num_server_alr = 0
        remove_num = 0
        done = 0
        players_to_be = []
        added_to_server_tracking = []
        removed_from_server_tracking = []
        for player in country:
            if str(player.league) == "Legend League":
                players_to_be.append(player.tag)
                is_global_tracked = await check_global_tracked(player=player)
                is_server_tracked = await check_server_tracked(player=player, server_id=ctx.guild.id)
                if is_global_tracked:
                    num_global_alr +=1
                if is_server_tracked:
                    num_server_alr += 1
                if not is_global_tracked:
                    num_global_tracked += 1
                    clan_name = "No Clan"
                    if player.clan is not None:
                        clan_name = player.clan.name
                    await addLegendsPlayer_GLOBAL(player=player,clan_name=clan_name)
                if not is_server_tracked:
                    num_server_tracked+=1
                    added_to_server_tracking.append(player.tag)
                    await addLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)
                done += 1
                if done == top:
                    break

        if chose == "Yes":
            tracked_members = results.get("tracked_members")
            for mem in tracked_members:
                if mem not in players_to_be:
                    remove_num += 1
                    removed_from_server_tracking.append(mem)
                    await ongoing_stats.update_one({'tag': mem},
                                                   {'$pull': {"servers": ctx.guild.id}})
                    await server_db.update_one({'server': ctx.guild.id},
                                               {'$pull': {"tracked_members": mem}})

        page_buttons = [
            disnake.ui.Button(label=translate("revert", ctx), emoji=partial_emoji_gen(self.bot, fetch_emojis("Legends History")),
                              style=disnake.ButtonStyle.red,
                              custom_id="Revert")]
        buttons = disnake.ui.ActionRow()
        buttons.append_item(page_buttons[0])

        embed = disnake.Embed(title=f"Location: {country_name}, Top {top}",
            description=f"{translate('global_tracking',ctx)}: {num_global_tracked} {translate('added',ctx)} | {num_global_alr} {translate('already_present',ctx)}\n"
                        f"{translate('server_tracking',ctx)}: {num_server_tracked} {translate('added',ctx)} | {num_server_alr} {translate('already_present',ctx)}\n"
                        f"{remove_num} {translate('removed_server_tracking', ctx)}",
            color=disnake.Color.green())
        embed.set_footer(text=translate("10_min_revert", ctx))
        if ctx.guild.icon is not None:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        await msg.edit(embed=embed, components=buttons)

        chose = False
        while chose is False:
            try:
                res: disnake.MessageInteraction = await self.bot.wait_for("message_interaction", check=check,
                                                                          timeout=600)
            except:
                await msg.edit(components=[])
                break

            if res.author.id != ctx.author.id:
                await res.send(content=translate("must_run_interact", ctx), ephemeral=True)
                continue

            if res.data.custom_id == "Revert":
                await res.response.defer()
                for tag in added_to_server_tracking:
                    await removeLegendsPlayer_SERVER(ctx.guild_id, None, tag)
                for tag in removed_from_server_tracking:
                    await addLegendsPlayer_SERVER(ctx.guild_id, None, tag)
                embed = disnake.Embed(description=translate("server_tracking_reverted", ctx).format(country_name=country_name),
                                      color=disnake.Color.green())
                return await res.edit_original_message(embed=embed,
                                                       components=[])



    async def create_lb(self, location_id, ctx):

        if location_id == "global":
            country = await coc_client.get_location_players(location_id="global")
            country_name = "Global"
        else:
            location_id = int(location_id)
            country = await coc_client.get_location_players(location_id=location_id)
            country_name = await coc_client.get_location(location_id)

        x = 1
        text = ""
        embeds = []
        y = 0
        for member in country:
            rank = str(x) + "."
            rank = rank.ljust(3)
            x +=1
            person = await ongoing_stats.find_one({'tag': member.tag})
            name = emoji.get_emoji_regexp().sub('', member.name)
            hit_text = " "
            if person is not None:
                hits = person.get("today_hits")
                hits = sum(hits)
                numHits = person.get("num_today_hits")
                defs = person.get("today_defenses")
                numDefs = len(defs)
                defs = sum(defs)
                if numHits > 9:
                    numHits = 9
                if numDefs > 9:
                    numDefs = 9
                numHits = SUPER_SCRIPTS[numHits]
                numDefs = SUPER_SCRIPTS[numDefs]
                hit_text = f"\n` ➼ ` <:sword:825589136026501160> {hits}{numHits} <:clash:877681427129458739> {defs}{numDefs}"

            text += f"`{rank}`\u200e**<:trophyy:849144172698402817>\u200e{member.trophies} | \u200e{name}**{hit_text}\n"
            y += 1
            if y == 30:
                embed = disnake.Embed(title=f"**{country_name} {translate('legend_lb', ctx)}**",
                                      description=text)
                y = 0
                embeds.append(embed)
                text = ""

        if text != "":
            embed = disnake.Embed(title=f"**{country_name} {translate('legend_lb', ctx)}**",
                                  description=text)
            embeds.append(embed)

        if text == "" and embeds == []:
            text = translate("no_players", ctx)
            embed = disnake.Embed(title=f"**{country_name} {translate('legend_lb', ctx)}**",
                                  description=text)
            embeds.append(embed)

        return embeds

    @country_lb.autocomplete("country")
    @country_track.autocomplete("country")
    async def autocomp_names(self, inter:disnake.ApplicationCommandInteraction, user_input: str):
        query = user_input.lower()
        query = re.escape(query)
        names = []
        results = locations.find({"country_name": {"$regex": f"^(?i).*{query}.*$"}})
        for document in await results.to_list(length=25):
            names.append(document.get("country_name"))
        return names