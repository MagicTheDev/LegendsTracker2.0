
from disnake.ext import commands, tasks
from utils.helper import profile_db, ongoing_stats, translate
import datetime as dt
import emoji
SUPER_SCRIPTS=["⁰","¹","²","³","⁴","⁵","⁶", "⁷","⁸", "⁹"]
import disnake

class DMFeed(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.dm_check.start()


    def cog_unload(self):
        self.dm_check.cancel()

    @commands.slash_command(name="daily_report", description="Opt in/out of daily report on tracked players sent to your dm.")
    async def daily_report(self, ctx: disnake.ApplicationCommandInteraction, opt = commands.Param(description="Opt In/Out",choices=["Opt-In", "Opt-Out"])):
        results = await profile_db.find_one({'discord_id': ctx.author.id})
        if results is None:
            if opt == "Opt-In":
                try:
                    await ctx.author.send(content=translate("opted_in_no_track", ctx))
                    await ctx.send(content=translate("opted_in_no_track", ctx), ephemeral=True)
                except:
                    return await ctx.send(content="Could not send you a dm. Make sure you have dm's enabled.\n"
                                           "`User Settings> Privacy & Safety> Toggle “Allow DMs from server members”`", ephemeral=True)
            else:
                await ctx.send(content=translate("opted_out",ctx), ephemeral=True)

            await profile_db.insert_one({'discord_id': ctx.author.id,
                                         "profile_tags": [],
                                         "opt": opt})
        else:
            profile_tags = results.get("profile_tags")
            if opt == "Opt-In" and profile_tags == []:
                try:
                    await ctx.author.send(content=translate("opted_in_no_track", ctx))
                    await ctx.send(content=translate("opted_in_no_track", ctx),ephemeral=True)
                except:
                    return await ctx.send(content="Could not send you a dm. Make sure you have dm's enabled.\n"
                                           "`User Settings> Privacy & Safety> Toggle “Allow DMs from server members”`", ephemeral=True)
            elif opt == "Opt-In":
                try:
                    await ctx.author.send(content=translate("opted_in", ctx))
                    await ctx.send(content=translate("opted_in", ctx),ephemeral=True)
                except:
                    return await ctx.send(content="Could not send you a dm. Make sure you have dm's enabled.\n"
                                           "`User Settings> Privacy & Safety> Toggle “Allow DMs from server members”`", ephemeral=True)
            else:
                await ctx.send(content=translate("opted_out", ctx), ephemeral=True)

            await profile_db.update_one({'discord_id': ctx.author.id},
                                        {'$set': {"opt": opt}})


    @tasks.loop(seconds=60)
    async def dm_check(self):
        now = dt.datetime.utcnow()
        hour = now.hour
        minute = now.minute
        if hour == 4 and minute == 55:
            results = profile_db.find({"opt": "Opt-In"})
            limit = await profile_db.count_documents(filter={"opt": "Opt-In"})
            for document in await results.to_list(length=limit):
                tracked_players = document.get("profile_tags")
                user_id = document.get("discord_id")
                button = disnake.ui.Button(label="Opt Out", style=disnake.ButtonStyle.red, custom_id=f"dm_{user_id}")
                buttons = disnake.ui.ActionRow()
                buttons.append_item(button)
                if len(tracked_players) == 0:
                    continue
                ranking = []
                for member in tracked_players:
                    person = await ongoing_stats.find_one({'tag': member})
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
                initial = f"__**{translate('daily_report', None, user_id)}**__"
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
                    text += f"\u200e**<:trophyy:849144172698402817>{trophies} | \u200e{name}**\n➼ <:cw:948845649229647952> {hits}{numHits} <:sh:948845842809360424> {defs}{numDefs}\n"

                embed = disnake.Embed(title=initial,
                                      description=text)
                embed.set_footer(text=translate("opt_out_time", None, user_id))
                user = await self.bot.get_or_fetch_user(user_id=user_id)
                try:
                    await user.send(embed=embed, components=[buttons])
                except:
                    continue

    @commands.Cog.listener()
    async def on_message_interaction(self, res: disnake.MessageInteraction):
        if "dm" in res.data.custom_id:
            data = res.data.custom_id
            data = data.split("_")
            user_id = data[1]
            await profile_db.update_one({'discord_id': int(user_id)},
                                        {'$set': {"opt": "Opt-Out"}})
            await res.send(content=translate("opted_out_button", None, user_id), ephemeral=True)

    @dm_check.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(DMFeed(bot))
