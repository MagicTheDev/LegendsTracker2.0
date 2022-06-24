from disnake.ext import commands
from utils.helper import server_db, ongoing_stats, translate, has_single_plan, has_guild_plan, decrement_usage
from utils.components import leaderboard_components
import disnake
import emoji

SUPER_SCRIPTS=["⁰","¹","²","³","⁴","⁵","⁶", "⁷","⁸", "⁹"]

class ServerLeaderboard(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.slash_command(name="leaderboard", description="Server Legends leaderboard (text)")
    async def leaderboard(self, ctx: disnake.ApplicationCommandInteraction):
        SINGLE_PLAN = await has_single_plan(ctx)
        GUILD_PLAN = await has_guild_plan(ctx)
        TIER, NUM_COMMANDS, MESSAGE = await decrement_usage(ctx, SINGLE_PLAN, GUILD_PLAN)
        if MESSAGE is not None:
            await ctx.response.defer(ephemeral=True)
            return await ctx.send(content=MESSAGE)

        await ctx.response.defer()
        results = await server_db.find_one({'server': ctx.guild.id})
        tracked_members = results.get("tracked_members")
        if len(tracked_members) == 0:
            return None

        ranking = []
        tracked = ongoing_stats.find({"tag": {"$in": tracked_members}})
        limit = await ongoing_stats.count_documents(filter={"tag": {"$in": tracked_members}})
        for person in await tracked.to_list(length=limit):
            #person = await ongoing_stats.find_one({'tag': member})

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

        ALPHABET = 0; STARTED = 1; OFFENSE = 2; DEFENSE = 4; TROPHIES = 6
        sort_types = {0 : "Alphabetically", 1: "by Start Trophies", 2 : "by Offense", 4 : "by Defense", 6 : "by Current Trophies"}
        sort_type = 6
        embeds = await self.create_embed(ctx, ranking)
        embed = embeds[0]
        embed.set_footer(text=f"Sorted {sort_types[sort_type]}")
        current_page = 0
        await ctx.edit_original_message(embed=embed, components=leaderboard_components(self.bot, current_page, embeds, ctx))
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
                    embed.set_footer(text=f"{translate('sorted',ctx)} {translate(sort_types[sort_type], ctx)}")
                    await res.response.edit_message(embed=embed,
                                                    components=leaderboard_components(self.bot, current_page, embeds, ctx))

                elif res.data.custom_id == "Next":
                    current_page += 1
                    embed = embeds[current_page]
                    embed.set_footer(text=f"{translate('sorted',ctx)} {translate(sort_types[sort_type], ctx)}")
                    await res.response.edit_message(embed=embed,
                                                    components=leaderboard_components(self.bot, current_page, embeds, ctx))
            else:
                current_page = 0
                sort_type = int(res.values[0])
                ranking = sorted(ranking, key=lambda l: l[int(res.values[0])], reverse=int(res.values[0])!=0 and int(res.values[0])!=4)
                embeds = await self.create_embed(ctx, ranking)
                embed = embeds[current_page]
                embed.set_footer(text=f"{translate('sorted',ctx)} {translate(sort_types[sort_type], ctx)}")
                await res.response.edit_message(embed=embed,
                                                components=leaderboard_components(self.bot, current_page, embeds, ctx))



    async def create_embed(self, ctx, ranking):
        text = ""
        initial = f"__**{ctx.guild.name} {translate('legend_lb', ctx)}**__\n"
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
                embed = disnake.Embed(title=f"**{ctx.guild} {translate('legend_lb', ctx)}**",
                                      description=text)
                if ctx.guild.icon is not None:
                    embed.set_thumbnail(url=ctx.guild.icon.url)
                x = 0
                embeds.append(embed)
                text = ""

        if text != "":
            embed = disnake.Embed(title=f"**{ctx.guild} {translate('legend_lb', ctx)}**",
                                  description=text)
            if ctx.guild.icon is not None:
                embed.set_thumbnail(url=ctx.guild.icon.url)
            embeds.append(embed)
        return embeds




