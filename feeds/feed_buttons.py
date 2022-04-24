
from disnake.ext import commands
import disnake
from utils.helper import getPlayer, ongoing_stats, profile_db
stat_types = ["Previous Days", "Legends Overview", "Graph & Stats", "Legends History", "Add to Quick Check"]
from coc import utils
from dbplayer import DB_Player


class FeedButtons(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
      

    @commands.Cog.listener()
    async def on_dropdown(self, ctx: disnake.MessageInteraction):
        if utils.is_valid_tag(ctx.values[0]):
            tags = [ctx.values[0]]
            view = disnake.ui.View.from_message(ctx.message)
            await ctx.response.edit_original_message(view=view)

            ez_look = False
            check = self.bot.get_cog("MainCheck")
            current_page = 0
            stats_page = []
            trophy_results = []

            x = 0
            results = []
            is_many = len(tags) > 1
            if is_many and ez_look:
                x = 1
            text = ""
            for tag in tags:
                r = await ongoing_stats.find_one({"tag": tag})
                results.append(r)
                player = DB_Player(r)
                SUPER_SCRIPTS = ["⁰", "¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹"]
                numHits = SUPER_SCRIPTS[player.num_hits]
                numDefs = SUPER_SCRIPTS[player.num_def]
                text += f"\u200e**<:trophyy:849144172698402817>{player.trophies} | \u200e{player.name}**\n➼ <:cw:948845649229647952> {player.sum_hits}{numHits} <:sh:948845842809360424> {player.sum_defs}{numDefs}\n"
                trophy_results.append(disnake.SelectOption(label=f"{player.name} | 🏆{player.trophies}", value=f"{x}"))
                embed = await check.checkEmbed(r)
                stats_page.append(embed)
                x += 1

            if is_many and ez_look:
                embed = disnake.Embed(title=f"{len(results)} Results",
                                      description=text)
                trophy_results.insert(0, disnake.SelectOption(label=f"Results Overview", value=f"0"))
                embed.set_footer(text="Use `Player Results` menu Below to switch btw players")
                stats_page.insert(0, embed)
                components = await self.create_components(results, trophy_results, current_page, is_many and ez_look)
                await ctx.send(embed=embed, components=components)
            else:
                components = await self.create_components(results, trophy_results, current_page, is_many and ez_look)
                await ctx.send(embed=stats_page[0], components=components)

            msg= await ctx.original_message()
            def check(res: disnake.MessageInteraction):
                return res.message.id == msg.id

            while True:
                try:
                    res: disnake.MessageInteraction = await self.bot.wait_for("message_interaction", check=check,
                                                                              timeout=600)
                except:
                    await msg.edit(components=[])
                    break

                if res.values[0] in stat_types:
                    if res.values[0] == "Add to Quick Check":
                        await self.add_profile(res, results[current_page], components, msg)
                    else:
                        current_stat = stat_types.index(res.values[0])
                        await res.response.defer()
                        embed = await self.display_embed(results, stat_types[current_stat], current_page)
                        await msg.edit(embed=embed,
                                       components=components)
                else:
                    try:
                        current_page = int(res.values[0])
                        embed = stats_page[current_page]
                        await res.response.edit_message(embed=embed,
                                                        components=components)
                    except:
                        continue

    @commands.Cog.listener()
    async def on_button_click(self, ctx: disnake.MessageInteraction):
        if ctx.component.label == "All Stats":
            tags = [ctx.component.custom_id]
            ez_look = False
            check = self.bot.get_cog("MainCheck")
            current_page = 0
            stats_page = []
            trophy_results = []

            x = 0
            results = []
            is_many = len(tags) > 1
            if is_many and ez_look:
                x = 1
            text = ""
            for tag in tags:
                r = await ongoing_stats.find_one({"tag": tag})
                results.append(r)
                player = DB_Player(r)
                SUPER_SCRIPTS = ["⁰", "¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹"]
                numHits = SUPER_SCRIPTS[player.num_hits]
                numDefs = SUPER_SCRIPTS[player.num_def]
                text += f"\u200e**<:trophyy:849144172698402817>{player.trophies} | \u200e{player.name}**\n➼ <:cw:948845649229647952> {player.sum_hits}{numHits} <:sh:948845842809360424> {player.sum_defs}{numDefs}\n"
                trophy_results.append(disnake.SelectOption(label=f"{player.name} | 🏆{player.trophies}", value=f"{x}"))
                embed = await check.checkEmbed(r)
                stats_page.append(embed)
                x += 1

            if is_many and ez_look:
                embed = disnake.Embed(title=f"{len(results)} Results",
                                      description=text)
                trophy_results.insert(0, disnake.SelectOption(label=f"Results Overview", value=f"0"))
                embed.set_footer(text="Use `Player Results` menu Below to switch btw players")
                stats_page.insert(0, embed)
                components = await self.create_components(results, trophy_results, current_page, is_many and ez_look)
                await ctx.send(embed=embed, components=components)
            else:
                components = await self.create_components(results, trophy_results, current_page, is_many and ez_look)
                await ctx.send(embed=stats_page[0], components=components)

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

                if res.values[0] in stat_types:
                    if res.values[0] == "Add to Quick Check":
                        await self.add_profile(res, results[current_page], components, msg)
                    else:
                        current_stat = stat_types.index(res.values[0])
                        await res.response.defer()
                        embed = await self.display_embed(results, stat_types[current_stat], current_page)
                        await msg.edit(embed=embed,
                                       components=components)
                else:
                    try:
                        current_page = int(res.values[0])
                        embed = stats_page[current_page]
                        await res.response.edit_message(embed=embed,
                                                        components=components)
                    except:
                        continue

    async def add_profile(self, res, tag, components, msg):
        tag = tag.get("tag")
        results = await profile_db.find_one({'discord_id': res.author.id})
        await msg.edit(components=components)
        if results is None:
            await profile_db.insert_one({'discord_id': res.author.id,
                                         "profile_tags": [f"{tag}"]})
            player = await getPlayer(tag)
            await res.send(content=f"Added {player.name} to your Quick Check list.", ephemeral=True)
        else:
            profile_tags = results.get("profile_tags")
            if tag in profile_tags:
                await profile_db.update_one({'discord_id': res.author.id},
                                            {'$pull': {"profile_tags": tag}})
                player = await getPlayer(tag)
                await res.send(content=f"Removed {player.name} from your Quick Check list.", ephemeral=True)
            else:
                if len(profile_tags) > 25:
                    await res.send(content=f"Can only have 25 players on your Quick Check list. Please remove one.",
                                   ephemeral=True)
                else:
                    await profile_db.update_one({'discord_id': res.author.id},
                                                {'$push': {"profile_tags": tag}})
                    player = await getPlayer(tag)
                    await res.send(content=f"Added {player.name} to your Quick Check list.", ephemeral=True)

    async def display_embed(self, results, stat_type, current_page):

        check = self.bot.get_cog("MainCheck")

        if stat_type == "Legends Overview":
            return await check.checkEmbed(results[current_page])
        elif stat_type == "Previous Days":
            return await check.checkYEmbed(results[current_page])
        elif stat_type == "Graph & Stats":
            return await check.createGraphEmbed(results[current_page])
        elif stat_type == "Legends History":
            return await check.create_history(results[current_page].get("tag"))

    async def create_components(self, results, trophy_results, current_page, is_many):
        length = len(results)
        options = []

        for stat in stat_types:
            if stat == "Add to Quick Check":
                options.append(disnake.SelectOption(label=f"{stat}", value=f"{stat}",
                                                    description="(If already added, will remove player instead)"))
            else:
                options.append(disnake.SelectOption(label=f"{stat}", value=f"{stat}"))

        stat_select = disnake.ui.Select(
            options=options,
            placeholder="Stat Pages & Settings",
            min_values=1,  # the minimum number of options a user must select
            max_values=1  # the maximum number of options a user can select
        )
        st = disnake.ui.ActionRow()
        st.append_item(stat_select)

        if length == 1:
            return st

        profile_select = disnake.ui.Select(
            options=trophy_results,
            placeholder="Player Results",
            min_values=1,  # the minimum number of options a user must select
            max_values=1  # the maximum number of options a user can select
        )
        st2 = disnake.ui.ActionRow()
        st2.append_item(profile_select)

        if is_many and current_page == 0:
            return [st2]

        return [st, st2]


def setup(bot):
    bot.add_cog(FeedButtons(bot))
