import disnake
from disnake.ext import commands
from utils.helper import ongoing_stats, profile_db, getPlayer, translate
from utils.discord import partial_emoji_gen
from utils.emojis import fetch_emojis
from dbplayer import DB_Player

stat_types = ["Previous Days", "Legends Overview", "Graph & Stats", "Legends History", "Quick Check & Daily Report Add", "Quick Check & Daily Report Remove"]

class Pagination(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def button_pagination(self, msg, tags, ez_look, ctx):
        check = self.bot.get_cog("MainCheck")
        current_page = 0
        stats_page = []
        trophy_results = []

        x=0
        results = []
        is_many = len(tags) > 1
        if is_many and ez_look:
            results.append("x")
            x= 1
        text = ""
        for tag in tags:
            r = await ongoing_stats.find_one({"tag": tag})
            results.append(r)
            player = DB_Player(r)
            SUPER_SCRIPTS = ["⁰", "¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹"]
            try:
                numHits = SUPER_SCRIPTS[player.num_hits]
            except:
                numHits = "⁸"
            try:
                numDefs = SUPER_SCRIPTS[player.num_def]
            except:
                numDefs = "⁸"
            text += f"\u200e**<:trophyy:849144172698402817>{player.trophies} | \u200e{player.name}**\n➼ <:cw:948845649229647952> {player.sum_hits}{numHits} <:sh:948845842809360424> {player.sum_defs}{numDefs}\n"
            th_emoji = partial_emoji_gen(self.bot, fetch_emojis(int(player.town_hall)))
            trophy_results.append(disnake.SelectOption(label=f"{player.name} | 🏆{player.trophies}", value=f"{x}", emoji=th_emoji))
            embed = await check.checkEmbed(r, ctx)
            stats_page.append(embed)
            x+=1

        if is_many and ez_look:
            embed = disnake.Embed(title=f"{len(results)-1} {translate('results',ctx)}",
                                  description=text)
            r_emoji = partial_emoji_gen(self.bot, fetch_emojis("pin"))
            trophy_results.insert(0, disnake.SelectOption(label=translate("results_overview",ctx), value=f"0", emoji=r_emoji))
            embed.set_footer(text=translate("switch_tip", ctx))
            stats_page.insert(0, embed)
            components = await self.create_components(results, trophy_results, current_page, is_many and ez_look, ctx)
            await msg.edit(embed=embed, components=components)
        else:
            components = await self.create_components(results, trophy_results, current_page, is_many and ez_look, ctx)
            await msg.edit(embed=stats_page[0], components=components)

        def check(res: disnake.MessageInteraction):
            return res.message.id == msg.id

        while True:
            try:
                res: disnake.MessageInteraction = await self.bot.wait_for("message_interaction", check=check, timeout=600)
            except:
                await msg.edit(components=[])
                break

            if res.values[0] in stat_types:
                if "Quick Check & Daily Report" in res.values[0]:
                    await self.add_profile(res, results[current_page], msg, trophy_results, current_page, is_many and ez_look, results)
                else:
                    current_stat = stat_types.index(res.values[0])
                    await res.response.defer()
                    embed = await self.display_embed(results, stat_types[current_stat], current_page, ctx)
                    await msg.edit(embed=embed,
                                   components=components)
            else:
                try:
                    previous_page = current_page
                    current_page = int(res.values[0])
                    components = await self.create_components(results, trophy_results, current_page, is_many and ez_look, res)
                    embed = stats_page[current_page]
                    await res.response.edit_message(embed=embed,
                                   components=components)
                except:
                    continue


    async def add_profile(self, res, tag, msg, trophy_results, current_page, is_true, rresult):
        tag = tag.get("tag")
        results = await profile_db.find_one({'discord_id': res.author.id})
        if results is None:
            await profile_db.insert_one({'discord_id': res.author.id,
                                         "profile_tags" : [f"{tag}"]})
            player = await getPlayer(tag)
            await res.send(content=f"Added {player.name} to your Quick Check & Daily Report list.", ephemeral=True)
        else:
            profile_tags = results.get("profile_tags")
            if tag in profile_tags:
                await profile_db.update_one({'discord_id': res.author.id},
                                               {'$pull': {"profile_tags": tag}})
                player = await getPlayer(tag)
                await res.send(content=f"Removed {player.name} from your Quick Check & Daily Report list.", ephemeral=True)
            else:
                if len(profile_tags) > 24:
                    await res.send(content=f"Can only have 24 players on your Quick Check & Daily Report list. Please remove one.", ephemeral=True)
                else:
                    await profile_db.update_one({'discord_id': res.author.id},
                                               {'$push': {"profile_tags": tag}})
                    player = await getPlayer(tag)
                    await res.send(content=f"Added {player.name} to your Quick Check & Daily Report list.", ephemeral=True)

        components = await self.create_components(rresult, trophy_results, current_page, is_true, res)
        await msg.edit(components=components)

    async def display_embed(self, results, stat_type, current_page, ctx):

        check = self.bot.get_cog("MainCheck")

        if stat_type == "Legends Overview":
            return await check.checkEmbed(results[current_page], ctx)
        elif stat_type == "Previous Days":
            return await check.checkYEmbed(results[current_page], ctx)
        elif stat_type == "Graph & Stats":
            return await check.createGraphEmbed(results[current_page], ctx)
        elif stat_type == "Legends History":
            return await check.create_history(results[current_page].get("tag"), ctx)

    async def create_components(self, results, trophy_results, current_page, is_many, ctx):
        length = len(results)
        options = []
        for stat in stat_types:
            if stat == "Quick Check & Daily Report Add":
                presults = await profile_db.find_one({'discord_id': ctx.author.id})
                if presults is None:
                    continue
                tags = presults.get("profile_tags")
                result = results[current_page]
                if result == "x":
                    continue
                tag = result.get("tag")
                if tag in tags:
                    continue
                emoji = partial_emoji_gen(self.bot, fetch_emojis("quick_check"))
                options.append(disnake.SelectOption(label=f"{stat}", value=f"{stat}", emoji=emoji))
            elif stat == "Quick Check & Daily Report Remove":
                presults = await profile_db.find_one({'discord_id': ctx.author.id})
                if presults is None:
                    continue
                tags = presults.get("profile_tags")
                result = results[current_page]
                if result == "x":
                    continue
                tag = result.get("tag")
                if tag in tags:
                    emoji = partial_emoji_gen(self.bot, fetch_emojis("quick_check"))
                    options.append(disnake.SelectOption(label=f"{stat}", value=f"{stat}", emoji=emoji))
            else:
                emoji = partial_emoji_gen(self.bot, fetch_emojis(stat))
                old_stat = stat
                stat = translate(stat, ctx)
                options.append(disnake.SelectOption(label=f"{stat}", value=f"{old_stat}", emoji=emoji))

        stat_select = disnake.ui.Select(
            options=options,
            placeholder=f"⚙️ {translate('player_results',ctx)}",
            min_values=1,  # the minimum number of options a user must select
            max_values=1  # the maximum number of options a user can select
        )
        st = disnake.ui.ActionRow()
        st.append_item(stat_select)

        if length == 1:
            return st

        profile_select = disnake.ui.Select(
            options=trophy_results,
            placeholder=f"🔎 {translate('stat_page_setting',ctx)}",
            min_values=1,  # the minimum number of options a user must select
            max_values=1  # the maximum number of options a user can select
        )
        st2 = disnake.ui.ActionRow()
        st2.append_item(profile_select)

        if is_many and current_page==0:
            return [st2]

        return[st, st2]

