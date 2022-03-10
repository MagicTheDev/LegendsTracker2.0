
from disnake.ext import commands
from utils.helper import coc_client, locations
from utils.db import *
from utils.components import create_components
SUPER_SCRIPTS=["⁰","¹","²","³","⁴","⁵","⁶", "⁷","⁸", "⁹"]
import emoji
import disnake
import re


class CountryLeaderboard(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def autocomp_names(self, query: str):
        query = query.lower()
        query = re.escape(query)
        names = []
        results = locations.find({"country_name": {"$regex": f"^(?i).*{query}.*$"}})
        for document in await results.to_list(length=25):
            names.append(document.get("country_name"))
        return names

    @commands.slash_command(name="country", description="test")
    async def country(self, ctx):
        pass

    @country.sub_command(name="leaderboards", description="Search country (or global) leaderboards")
    async def country_lb(self, ctx: disnake.ApplicationCommandInteraction , country: str = commands.Param(autocomplete=autocomp_names)):
        await ctx.response.defer()
        loc = await coc_client.get_location_named(country)
        if country == "Global":
            embeds = await self.create_lb("global")
        else:
            if loc is None:
                return await ctx.edit_original_message(content="Not a valid country. Use the autocomplete to help select from the 100+ countries.")
            embeds = await self.create_lb(loc.id)

        current_page = 0
        await ctx.edit_original_message(embed=embeds[0], components=create_components(current_page, embeds))
        msg = await ctx.original_message()
        def check(res: disnake.MessageInteraction):
            return res.message.id == msg.id

        while True:
            try:
                res = await self.bot.wait_for("message_interaction", check=check, timeout=600)
            except:
                await ctx.edit_original_message(components=[])
                break

            if res.author.id != ctx.author.id:
                await res.send(content="You must run the command to interact with components.", ephemeral=True)
                continue

            # print(res.custom_id)
            if res.data.custom_id == "Previous":
                current_page -= 1
                await res.response.edit_message(embed=embeds[current_page],
                               components=create_components(current_page, embeds))

            elif res.data.custom_id == "Next":
                current_page += 1
                await res.response.edit_message(embed=embeds[current_page],
                               components=create_components(current_page, embeds))



    @country.sub_command(name="track", description="Add players from country (or global) leaderboards")
    async def country_track(self,ctx: disnake.ApplicationCommandInteraction, country: str = commands.Param(autocomplete=autocomp_names), top: int = 200):
        """
            Parameters
            ----------
            country: Country to track
            top: Top # of players to track (1 - 200), default is 200
          """

        perms = ctx.author.guild_permissions.manage_guild
        if not perms:
            embed = disnake.Embed(description="Command requires `Manage Server` permissions.",
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)

        if top <= 0 or top >= 201:
            embed = disnake.Embed(description="Top number must be between 1 and 200.",
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)



        results = await server_db.find_one({"server": ctx.guild.id})
        tracked_members = results.get("tracked_members")
        feed = results.get("channel_id")
        if len(tracked_members) > 500 and feed is not None:
            embed = disnake.Embed(
                description="Sorry this command cannot be used while you have more than 500 people tracked and have feed enabled.\n"
                            "Please clear some members with `/clear_under`, sync members with `/clan_track sync`, or remove individual accounts with `/track remove`",
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

        embed = disnake.Embed(description=f"**Would you like to remove tracked players outside of this location?**\n"
                                          f"if **yes**, this will set your feed & leaderboard to just players in this location.\n",
                              color=disnake.Color.green())

        select1 = disnake.ui.Select(
            options=[
                disnake.SelectOption(label="Yes", value=f"Yes", emoji="✅"),
                disnake.SelectOption(label="No", value=f"No", emoji="❌")
            ],
            placeholder="Choose your option",
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

        while chose == False:
            try:
                res: disnake.MessageInteraction = await self.bot.wait_for("message_interaction", check=check,
                                                                          timeout=600)
            except:
                await msg.edit(components=[])
                break

            if res.author.id != ctx.author.id:
                await res.send(content="You must run the command to interact with components.", ephemeral=True)
                continue

            chose = res.values[0]


        embed = disnake.Embed(
            description="<a:loading:884400064313819146> Adding players...",
            color=disnake.Color.green())
        await msg.edit(embed=embed, components=[])

        num_global_tracked = 0
        num_global_alr = 0
        num_server_tracked = 0
        num_server_alr = 0
        remove_num = 0
        done = 0
        players_to_be = []
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
                    if player.clan != None:
                        clan_name = player.clan.name
                    await addLegendsPlayer_GLOBAL(player=player,clan_name=clan_name)
                if not is_server_tracked:
                    num_server_tracked+=1
                    await addLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)
                done += 1
                if done == top:
                    break

        if chose == "Yes":
            tracked_members = results.get("tracked_members")
            for mem in tracked_members:
                if mem not in players_to_be:
                    remove_num += 1
                    await ongoing_stats.update_one({'tag': mem},
                                                   {'$pull': {"servers": ctx.guild.id}})
                    await server_db.update_one({'server': ctx.guild.id},
                                               {'$pull': {"tracked_members": mem}})

        embed = disnake.Embed(title=f"Location: {country_name}, Top {top}",
            description=f"Global Tracking: {num_global_tracked} added | {num_global_alr} already present\n"
                        f"Server Tracking: {num_server_tracked} added | {num_server_alr} already present\n"
                        f"{remove_num} removed from server tracking.",
            color=disnake.Color.green())
        if ctx.guild.icon is not None:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        return await msg.edit(embed=embed, components=[])


    async def create_lb(self, location_id):

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
            if y == 20:
                embed = disnake.Embed(title=f"**{country_name} Legend Leaderboard**",
                                      description=text)
                y = 0
                embeds.append(embed)
                text = ""

        if text != "":
            embed = disnake.Embed(title=f"**{country_name} Legend Leaderboard**",
                                  description=text)
            embeds.append(embed)

        if text == "" and embeds == []:
            text = "No Players"
            embed = disnake.Embed(title=f"**{country_name} Legend Leaderboard**",
                                  description=text)
            embeds.append(embed)

        return embeds

