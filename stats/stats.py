from disnake.ext import commands
from utils.helper import ongoing_stats, server_db, IS_BETA
import disnake
import emoji
import time
import statcord
import psutil
from matplotlib import pyplot as plt
import io
import numpy as np

class LegendStats(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.up = time.time()
        #test comment
        if not IS_BETA:
            self.key = "statcord.com-rsmhOZRkiyBTI2C7z4i6"
            self.api = statcord.Client(self.bot, self.key, custom1=self.custom1)
            self.api.start_loop()

    @commands.Cog.listener()
    async def on_application_command(self, ctx):
        if not IS_BETA:
            self.api.command_run(ctx)

    async def custom1(self):
        members = await ongoing_stats.count_documents(filter={})
        return members


    @commands.slash_command(name="stats", description="View bot stats")
    async def stat(self, ctx):
        results = await server_db.find_one({"server": ctx.guild.id})
        feed = "None"

        if results != None:
            feed = results.get("webhook")

        status = "<:status_green:948031949140799568>"
        if str(feed) == "None":
            status = "<:status_red:948032012160204840>"

        number_tracked = await ongoing_stats.count_documents(filter={})
        number_tracked = "{:,}".format(number_tracked)
        days_tracking = await ongoing_stats.find_one({"tag": "#2QV029CVC"})
        try:
            days_tracking = len(days_tracking.get("end_of_day")) + 1
        except:
            days_tracking = 0

        uptime = time.time() - self.up
        uptime = time.strftime("%H hours %M minutes %S seconds", time.gmtime(uptime))

        me = self.bot.user.mention

        inservers = len(self.bot.guilds)
        members = 0
        for guild in self.bot.guilds:
            members += guild.member_count - 1

        members = "{:,}".format(members)

        mem = psutil.virtual_memory()
        mem_used = mem.used
        mem_used = int(mem_used / 1000000)
        mem_used  = "{:,}".format(mem_used)
        mem_load = str(mem.percent)
        cpu_load = str(psutil.cpu_percent())

        current_bandwidth = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        current_bandwidth = int(current_bandwidth/1000)
        current_bandwidth = round(current_bandwidth /1000000, 2)


        embed = disnake.Embed(title='LegendsTracker Stats',
                              description=f"[Statcord Link](https://beta.statcord.com/bot/825324351016534036)\n"
                                          f"<:bot:862911608140333086> Bot: {me}\n" +
                                          f"<:discord:840749695466864650> Bot Ping: {round(self.bot.latency * 1000, 2)} ms\n"
                                          f"<:brain:948033339061846018> Memory Used: {mem_used}MB, {mem_load}%\n"
                                          f"<a:cpu:948033115199262824> CPU Load: {cpu_load}%\n"
                                          f"<:server:863148364006031422> In {str(inservers)} servers\n" +
                                          f"<a:num:863149480819949568> Watching {members} users\n" +
                                          f"<a:check:861157797134729256> {number_tracked} legends accounts tracked\n"+
                                          f"📆 {days_tracking} days spent tracking.\n"+
                                          f"🕐 Uptime: {uptime}\n"+
                                          f"Feed Operational: {status}",
                              color=disnake.Color.blue())

        await ctx.send(embed=embed)

    @commands.slash_command(name="streaks",description="View the top 3 star streak statistics.")
    async def streaks(self, ctx: disnake.ApplicationCommandInteraction):
        fire = "<a:fireflame:946369467561172993>"
        fire = ''.join(filter(str.isdigit, fire))
        fire = self.bot.get_emoji(int(fire))
        fire = disnake.PartialEmoji(name=fire.name, id=fire.id, animated=True)

        select = disnake.ui.Select(
            options=[  # the options in your dropdown
                disnake.SelectOption(label="All Triple Streaks",emoji=fire, value="1"),
                disnake.SelectOption(label="Server Triple Streaks",emoji=fire, value="2"),
                disnake.SelectOption(label="All Time Streak Leaderboard",emoji=fire, value="3"),
            ],
            placeholder="Choose your option",  # the placeholder text to show when no options have been chosen
            min_values=1,  # the minimum number of options a user must select
            max_values=1,  # the maximum number of options a user can select
        )

        embed1 = await self.streaks_global(ctx)
        embed2 = await self.streaks_local(ctx)
        embed3 = await self.streaks_lb(ctx)

        embeds = [embed1, embed2, embed3]

        st = disnake.ui.ActionRow()
        st.append_item(select)

        await ctx.send(embed=embed1, components=[st])

        msg = await ctx.original_message()

        def check(res: disnake.MessageInteraction):
            return res.message.id == msg.id

        while True:
            try:
                res = await self.bot.wait_for("message_interaction", check=check, timeout=600)
            except:
                await ctx.edit_original_message(components=[])
                break

            await res.response.edit_message(embed=embeds[int(res.values[0]) - 1])

    async def streaks_local(self, ctx):
        results = await server_db.find_one({"server": ctx.guild.id})
        tracked_members = results.get("tracked_members")

        results = []
        for member in tracked_members:
            player = await ongoing_stats.find_one({"tag": member})
            if player is None:
                await server_db.update_one({'server': ctx.guild.id},
                                           {'$pull': {"tracked_members": member}})
                continue
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

        board = disnake.Embed(title="🔥 Top 25 Server 3 Star Streaks 🔥 \n", description=text,
                              color=disnake.Color.blue())
        return board


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

        board = disnake.Embed(title="🔥 Top 25 Ongoing 3 Star Streaks 🔥 \n",
                              description=text,
                              color=disnake.Color.blue())
        return board

    async def streaks_lb(self, ctx):
        tracked = ongoing_stats.find({"highest_streak": {"$gte": 2}})
        limit = await ongoing_stats.count_documents(filter={"highest_streak": {"$gte": 2}})
        results = []
        for player in await tracked.to_list(length=limit):
            thisPlayer = []
            numberOfTriples = player.get("highest_streak")
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

        board = disnake.Embed(title="🔥 Top 25 **All Time** 3 Star Streaks 🔥 \n",
                              description=text,
                              color=disnake.Color.blue())
        return board

    @commands.slash_command(name="popular", description="View popular tracked players")
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

        board = disnake.Embed(title="🔥 Most popular tracked players 🔥 \n",
                              description=topTen,
                              color=disnake.Color.blue())
        await ctx.send(embed=board)


    @commands.slash_command(name="breakdown",description="Trophy Breakdown for players tracked.")
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

        board = disnake.Embed(title="Trophy Breakdown for players tracked.", description=text,
                              color=disnake.Color.blue())
        await ctx.send(embed=board)

