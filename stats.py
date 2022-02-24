from discord.ext import commands
from helper import getPlayer, ongoing_stats, server_db
import discord
import emoji
import time
from datetime import timedelta
from discord_slash import cog_ext
import statcord


class legend_stats(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.up = time.time()
        #test comment
        self.key = "statcord.com-rsmhOZRkiyBTI2C7z4i6"
        self.api = statcord.Client(self.bot, self.key, custom1=self.custom1)
        self.api.start_loop()

    @commands.Cog.listener()
    async def on_slash_command(self, ctx):
        self.api.command_run(ctx)

    async def custom1(self):
        members = await ongoing_stats.count_documents(filter={})
        return members


    @cog_ext.cog_slash(name="stats",
                       description="View bot stats.")
    async def stat(self, ctx):
        results = await server_db.find_one({"server": ctx.guild.id})

        feed = "None"

        if results != None:
            feed = results.get("channel_id")

        if str(feed) != "None":
            guild = ctx.guild.id
            guild = await self.bot.fetch_guild(guild)
            channels = await guild.fetch_channels()
            feed = discord.utils.get(channels,id=int(feed))
            feed = feed.mention

        number_tracked = await ongoing_stats.count_documents(filter={})
        days_tracking = await ongoing_stats.find_one({"tag": "#2QV029CVC"})
        try:
            days_tracking = len(days_tracking.get("end_of_day")) + 1
        except:
            days_tracking = 0

        uptime = time.time() - self.up
        uptime = time.strftime("%H hours %M minutes %S seconds", time.gmtime(uptime))

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
                              description=f"[Statcord Link](https://beta.statcord.com/bot/825324351016534036)\n"
                                          f"<:bot:862911608140333086> Bot: {me}\n" +
                                          f"<:discord:840749695466864650> Bot Ping: {round(self.bot.latency * 1000, 2)} ms\n" +
                                          f"<:clash:855491735488036904> COC Api Ping: {cocping} ms\n" +
                                          f"<:server:863148364006031422> In {str(inservers)} servers\n" +
                                          f"<a:num:863149480819949568> Watching {members} users\n" +
                                          f"<a:check:861157797134729256> {number_tracked} accounts tracked\n"+
                                          f"📆 {days_tracking} days spent tracking.\n"+
                                          f"🕐 Uptime: {uptime}\n"+
                                          f"Feed Channel: {feed}",
                              color=discord.Color.blue())

        await ctx.send(embed=embed)


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


    @cog_ext.cog_slash(name="breakdown",
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
                results[10]+=1

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