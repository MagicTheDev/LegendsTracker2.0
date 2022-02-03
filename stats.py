from discord.ext import commands
from clashClient import getPlayer, getClan
import discord
import emoji
import time
from datetime import timedelta

import speedtest

import certifi
ca = certifi.where()

import motor.motor_asyncio
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
ongoing_db = client.legends_stats
ongoing_stats = ongoing_db.ongoing_stats
settings = ongoing_db.settings

class legend_stats(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.up = time.time()

    @commands.command(name="stats", aliases=["stat"])
    async def stat(self, ctx):
        results = await settings.find_one({"server_id": ctx.guild.id})

        feed = "None"
        tlimit = "None"

        if results == None:
            feed = "None"
        else:
            feed =results.get("channel_id")
            tlimit = results.get("feedlimit")

        if str(feed) == "None":
            feed = "None"
            tlimit = "None"

        #print(feed)
        if str(feed) != "None":
            guild = ctx.guild.id
            guild = await self.bot.fetch_guild(guild)
            channels = await guild.fetch_channels()
            #print(feed)
            feed = discord.utils.get(channels,id=int(feed))
            feed = feed.mention


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
                                          f"🕐 Uptime: {uptime}\n"+
                                          f"Feed Channel: {feed}\n"+
                                          f"Feed TrophyLimit: {tlimit}",
                              color=discord.Color.blue())

        await msg.edit(content="", embed=embed)

    @commands.command(name='streak', aliases=["streaks"])
    async def streaks(self, ctx):
        board = discord.Embed(description="This command is down for the moment, being reworked & updated.", color=discord.Color.blue())
        return await ctx.send(embed=board)
        tracked = ongoing_stats.find({"row_triple" : {"$gte" : 3}})
        limit = await ongoing_stats.count_documents(filter={"row_triple" : {"$gte" : 3}})
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

        board = discord.Embed(title="🔥 Ongoing 3 Star Streaks 🔥 \n", description="(3 or more triples in a row)\n"+text,
                              color=discord.Color.blue())
        await ctx.send(embed=board)

    @commands.command(name= "popular")
    async def popular(self, ctx):
        tracked = ongoing_stats.find()
        limit = await ongoing_stats.count_documents(filter={})
        playerStats = []
        for document in await tracked.to_list(length=limit):
            player = []
            servers = document.get("servers")
            name = document.get("name")
            tag = document.get("tag")
            player.append(name)
            player.append(tag)
            player.append(len(servers))
            playerStats.append(player)

        playerStats.sort(key=lambda row: (row[2]), reverse=True)
        topTen = "**Name | Tag | # of servers tracked in**\n"
        for x in range (0,10):
            topTen+=f"{playerStats[x][0]} | {playerStats[x][1]} | {playerStats[x][2]}\n"

        board = discord.Embed(title="🔥 Most popular tracked players 🔥 \n",
                              description=topTen,
                              color=discord.Color.blue())
        await ctx.send(embed=board)

    @commands.command(name='lstats')
    async def legendStats(self, ctx):

        # 5000, 5100, 5200, 5300, 5400, 5500, 5600, 5700, 5800, 5900, 6000+
        legendsHits = [[], [], [], [], [], [], [], [], [], [], []]
        legendsDef = [[], [], [], [], [], [], [], [], [], [], []]
        legendsNet = [[], [], [], [], [], [], [], [], [], [], []]

        tracked = ongoing_stats.find()
        limit = await ongoing_stats.count_documents(filter={"league" : {"$eq" : "Legend League"}})
        playerStats = []
        for player in await tracked.to_list(length=limit):

            hits = player.get("previous_hits")
            defs = player.get("previous_defenses")

            today_hits = player.get("today_hits")
            today_def = player.get("today_defenses")

            today_net = sum(today_hits) - sum(today_def)

            trophy = player.get("trophies")
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

    @commands.command(name='breakdown')
    async def breakdown(self, ctx):

        results = [[], [], [], [], [], [], [], [], [], [], []]
        tracked = ongoing_stats.find()
        limit = await ongoing_stats.count_documents(filter={"league": {"$eq": "Legend League"}})
        playerStats = []
        for player in await tracked.to_list(length=limit):
            ct = player.get("trophies")

            if ct < 6000:
                spot = str(ct)
                spot = spot[1]
                spot = int(spot)
                results[spot].append(1)
            else:
                results[10].append(1)

        text = ""
        for x in range(0, 11):
            atRange = sum(results[x])
            if x <= 9:
                text += f"**5{x}00: ** {atRange}\n"
            else:
                text += f"**6000+:** {atRange}\n"

        board = discord.Embed(title="Trophy Breakdown for players tracked.", description=text,
                              color=discord.Color.blue())
        await ctx.send(embed=board)

    @commands.command(name="numbers")
    @commands.is_owner()
    async def numbers(self, ctx):
        tracked = ongoing_stats.find()
        limit = await ongoing_stats.count_documents(filter={})
        serverList = []
        count = []
        for document in await tracked.to_list(length=limit):

            servers = document.get("servers")

            for server in servers:
                if server not in serverList:
                    serverList.append(server)
                    count.append(1)
                else:
                    ind = serverList.index(server)
                    count[ind] += 1

        topTen = ""
        for x in range(0, len(serverList)):
            guild = await self.bot.fetch_guild(serverList[x])
            topTen += f"{guild.name} | {count[x]}\n"
            
              
        board = discord.Embed(title="**Numbers Tracked by Server**",
                                    description=topTen,
                                    color=discord.Color.blue())
        await ctx.send(embed=board)

    @commands.command(name="cleanup")
    @commands.is_owner()
    async def cleanup(self, ctx):
        tracked = ongoing_stats.find()
        limit = await ongoing_stats.count_documents(filter={})
        for document in await tracked.to_list(length=limit):
            tag = document.get("tag")
            today_hits = document.get("today_hits")
            for hit in today_hits:
                if hit >=41:
                    await ongoing_stats.update_one({'tag': f"{tag}"},
                                                   {'$pull': {"today_hits": hit}})





    


def setup(bot: commands.Bot):
    bot.add_cog(legend_stats(bot))