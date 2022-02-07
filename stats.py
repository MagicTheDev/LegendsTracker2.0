from discord.ext import commands
from helper import getPlayer, getClan, ongoing_stats, server_db
import discord
import emoji
import time
from datetime import timedelta
from discord_slash import cog_ext



class legend_stats(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.up = time.time()

    @cog_ext.cog_slash(name="stats",
                       description="View bot stats.")
    async def stat(self, ctx):


        number_tracked = await ongoing_stats.count_documents(filter={})
        days_tracking = await ongoing_stats.find_one({"tag": "#2QV029CVC"})
        try:
            days_tracking = len(days_tracking.get("end_of_day")) + 1
        except:
            days_tracking = 0
        owner = await self.bot.fetch_user(706149153431879760)

        uptime = time.time() - self.up
        uptime = time.strftime("%H hours %M minutes %S seconds", time.gmtime(uptime))

        msg = await ctx.send("<a:loading:862934416137781248> Loading data...")
        bp = msg.created_at - ctx.message.created_at
        bp = (bp / timedelta(milliseconds=1))
        meping = bp

        me = self.bot.user.mention

        before = time.time()
        await getPlayer("#P2PQDW")
        after = time.time()
        cocping = round(((after - before) * 1000), 2)

        inservers = len(self.bot.guilds)
        members = 0
        for guild in self.bot.guilds:
            members += guild.member_count - 1

        embed = discord.Embed(title='LegendsTracker Stats',
                              description=f"<:bot:862911608140333086> Bot: {me}\n" +
                                          f"<a:crown:862912607005442088> Owner: {owner.mention}\n" +
                                          f"<:discord:840749695466864650> Discord Api Ping: {round(self.bot.latency * 1000, 2)} ms\n" +
                                          f"<a:ping:862916971711168562> Bot Ping: {round(meping, 2)} ms\n" +
                                          f"<:clash:855491735488036904> COC Api Ping: {cocping} ms\n" +
                                          f"<:server:863148364006031422> In {str(inservers)} servers\n" +
                                          f"<a:num:863149480819949568> Watching {members} users\n" +
                                          f"<a:check:861157797134729256> {number_tracked} accounts tracked\n"+
                                          f"📆 {days_tracking} days spent tracking.\n"+
                                          f"🕐 Uptime: {uptime}\n",
                              color=discord.Color.blue())

        await msg.edit(content="", embed=embed)



    @cog_ext.cog_subcommand(base="streaks",name="server",
                       description="View the top 3 star streaks in your server.")
    async def streaks_local(self, ctx):
        results = await server_db.find_one({"server": ctx.guild.id})
        tracked_members = results.get("tracked_members")

        results = []
        for member in tracked_members:
            player = await ongoing_stats.find_one({"tag": member})
            thisPlayer = []
            numberOfTriples = player.get("row_triple")
            name = player.get("name")
            if numberOfTriples >= 2:
                thisPlayer.append(name)
                thisPlayer.append(numberOfTriples)
                results.append(thisPlayer)


        ranking = sorted(results, key=lambda l: l[1], reverse=True)
        ranking = ranking[0:25]

        text = ""
        x = 1

        for person in ranking:
            name = person[0]
            name = emoji.get_emoji_regexp().sub(' ', name)
            name = f"{x}. {name}"
            name = name.ljust(15)
            streak = person[1]
            text += f"`{name}` | **{streak} perfect** streak\n"
            x += 1

        if text == "":
            text = "No Streaks in Progress."

        board = discord.Embed(title="🔥 Top 25 Server 3 Star Streaks 🔥 \n", description=text,
                              color=discord.Color.blue())
        await ctx.send(embed=board)



    @cog_ext.cog_subcommand(base="streaks", name="global",
                            description="View the top 3 star streaks among all tracked players.")
    async def streaks_global(self, ctx):
        tracked = ongoing_stats.find({"row_triple": {"$gte": 2}})
        limit = await ongoing_stats.count_documents(filter={"row_triple": {"$gte": 2}})
        results = []
        for player in await tracked.to_list(length=limit):
            thisPlayer = []
            numberOfTriples = player.get("row_triple")
            name = player.get("name")
            if numberOfTriples >= 2:
                thisPlayer.append(name)
                thisPlayer.append(numberOfTriples)
                results.append(thisPlayer)

        ranking = sorted(results, key=lambda l: l[1], reverse=True)

        ranking = ranking[0:25]
        text = ""
        x = 1

        for person in ranking:
            name = person[0]
            name = emoji.get_emoji_regexp().sub(' ', name)
            name = f"{x}. {name}"
            name = name.ljust(15)
            streak = person[1]
            text += f"`{name}` | **{streak} perfect** streak\n"
            x += 1

        if text == "":
            text = "No Streaks in Progress."

        board = discord.Embed(title="🔥 Top 25 Ongoing 3 Star Streaks 🔥 \n",
                              description=text,
                              color=discord.Color.blue())
        await ctx.send(embed=board)


    @cog_ext.cog_slash(name='migrate', guild_ids=[849364313156485120],
                 description="Move portion of bot.")
    async def migrate(self, ctx):
        await ctx.defer()
        tracked = server_db.find()
        limit = await server_db.count_documents(filter={})
        for document in await tracked.to_list(length=limit):
            server = document.get("server")
            tracked_mem = document.get("tracked_members")

            real = []
            for member in tracked_mem:
                if member not in real:
                    real.append(member)

            for member in tracked_mem:
                await server_db.update_one({'server': server},
                                           {'$pull': {"tracked_members": member}})

            for member in real:
                await server_db.update_one({'server': server},
                                           {'$push': {"tracked_members": member}})


        await ctx.send("DONE")



    @cog_ext.cog_slash(name="popular",
                       description="View popular tracked players.")
    async def popular(self, ctx):
        tracked = ongoing_stats.find()
        limit = await ongoing_stats.count_documents(filter={})
        playerStats = []
        for document in await tracked.to_list(length=limit):
            try:
                player = []
                servers = document.get("servers")
                name = document.get("name")
                tag = document.get("tag")
                player.append(name)
                player.append(tag)
                player.append(len(servers))
                playerStats.append(player)
            except:
                continue

        playerStats.sort(key=lambda row: (row[2]), reverse=True)
        topTen = "**Name | Tag | # of servers tracked in**\n"
        for x in range (0,10):
            topTen+=f"{playerStats[x][0]} | {playerStats[x][1]} | {playerStats[x][2]}\n"

        board = discord.Embed(title="🔥 Most popular tracked players 🔥 \n",
                              description=topTen,
                              color=discord.Color.blue())
        await ctx.send(embed=board)

    @cog_ext.cog_slash(name="legend_stats",
                       description="Stats on the state of tracked players.")
    async def legendStats(self, ctx):

        # 5000, 5100, 5200, 5300, 5400, 5500, 5600, 5700, 5800, 5900, 6000+
        legendsHits = [[], [], [], [], [], [], [], [], [], [], []]
        legendsDef = [[], [], [], [], [], [], [], [], [], [], []]
        legendsNet = [[], [], [], [], [], [], [], [], [], [], []]

        tracked = ongoing_stats.find({"league" : {"$eq" : "Legend League"}})
        limit = await ongoing_stats.count_documents(filter={"league" : {"$eq" : "Legend League"}})
        playerStats = []
        for player in await tracked.to_list(length=limit):

            hits = player.get("previous_hits")
            defs = player.get("previous_defenses")

            today_hits = player.get("today_hits")
            today_def = player.get("today_defenses")

            today_net = sum(today_hits) - sum(today_def)

            trophy = player.get("trophies")
            if trophy < 5000:
                continue
            started = trophy - today_net

            try:
              hits = sum(hits[-1])
            except:
              hits = 0

            try:
              defs = sum(defs[-1])
            except:
              defs = 0

            net = hits - defs            

            if started < 6000:
                spot = str(started)
                spot = spot[1]
                spot = int(spot)
                # print(spot)
                # print(legendsHits)
                if hits != 0:
                  legendsHits[spot].append(hits)
                if defs != 0:
                  legendsDef[spot].append(defs)
                
                if hits != 0 or defs != 0:
                  legendsNet[spot].append(net)
            else:
                spot = 10
                if hits != 0:
                  legendsHits[spot].append(hits)
                if defs != 0:
                  legendsDef[spot].append(defs)
                
                if hits != 0 or defs != 0:
                  legendsNet[spot].append(net)

        text = "Stats calculated using yesterday numbers.\n"

        for x in range(0, 11):
            lenHit = len(legendsDef[x])
            # print(legendsHits)
            if lenHit != 0:
                averageHit = sum(legendsHits[x]) / len(legendsNet[x])
                averageDef = sum(legendsDef[x]) / len(legendsDef[x])
                averageNet = averageHit - averageDef
                if x == 10:
                    text += f"**At 6000+**\n" \
                            f"- Avg Hit Total: {int(averageHit)} trophies\n" \
                            f"- Avg Def Total: {int(averageDef)} trophies\n" \
                            f"- Avg Net Gain: {int(averageNet)} trophies\n"
                else:
                    text += f"**At 5{x}00**\n" \
                            f"- Avg Hit Total: {int(averageHit)} trophies\n" \
                            f"- Avg Def Total: {int(averageDef)} trophies\n" \
                            f"- Avg Net Gain: {int(averageNet)} trophies\n"
            else:
                if x == 10:
                    text += f"**-- No Results for 6000+ --**\n"
                else:
                    text += f"**-- No Results for 5{x}00 --**\n"

        embed = discord.Embed(title="Average Stats by Trophy Counts", description=text,
                              color=discord.Color.blue())
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="trophy_breakdown",
                       description="Trophy Breakdown for players tracked.")
    async def breakdown(self, ctx):

        results = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        tracked = ongoing_stats.find({"league": {"$eq": "Legend League"}})
        limit = await ongoing_stats.count_documents(filter={"league": {"$eq": "Legend League"}})
        playerStats = []
        for player in await tracked.to_list(length=limit):
            ct = player.get("trophies")
            if ct < 5000:
                continue


            if ct < 6000:
                spot = str(ct)
                spot = spot[1]
                spot = int(spot)
                results[spot]+=1
            else:
                results[10].append(1)

        text = ""
        for x in range(0, 11):
            atRange = results[x]
            if x <= 9:
                text += f"**5{x}00: ** {atRange}\n"
            else:
                text += f"**6000+:** {atRange}\n"

        board = discord.Embed(title="Trophy Breakdown for players tracked.", description=text,
                              color=discord.Color.blue())
        await ctx.send(embed=board)



def setup(bot: commands.Bot):
    bot.add_cog(legend_stats(bot))