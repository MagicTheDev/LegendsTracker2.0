from disnake.ext import commands
from utils.helper import ongoing_stats, server_db, IS_BETA, history_db, has_single_plan, has_guild_plan, decrement_usage, coc_client, translate
import disnake
import emoji
import time
import statcord.client as sclient
import psutil
import matplotlib.pyplot as plt
import io
import calendar

class LegendStats(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.up = time.time()
        #test comment
        if not IS_BETA:
            self.key = "statcord.com-rsmhOZRkiyBTI2C7z4i6"
            self.api = sclient.Client(self.bot, self.key, custom1=self.custom1)
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

        if results is not None:
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
        SINGLE_PLAN = await has_single_plan(ctx)
        GUILD_PLAN = await has_guild_plan(ctx)
        TIER, NUM_COMMANDS, MESSAGE = await decrement_usage(ctx, SINGLE_PLAN, GUILD_PLAN)
        if MESSAGE is not None:
            await ctx.response.defer(ephemeral=True)
            return await ctx.send(content=MESSAGE)

        await ctx.response.defer()
        fire = "<a:fireflame:946369467561172993>"
        fire = ''.join(filter(str.isdigit, fire))
        fire = self.bot.get_emoji(int(fire))
        fire = disnake.PartialEmoji(name=fire.name, id=fire.id, animated=True)

        select = disnake.ui.Select(
            options=[  # the options in your dropdown
                disnake.SelectOption(label=translate("all_streaks", ctx),emoji=fire, value="1"),
                disnake.SelectOption(label=translate("server_streaks", ctx),emoji=fire, value="2"),
                disnake.SelectOption(label=translate("all_time_streaks", ctx),emoji=fire, value="3"),
            ],
            placeholder=translate("choose_option", ctx),  # the placeholder text to show when no options have been chosen
            min_values=1,  # the minimum number of options a user must select
            max_values=1,  # the maximum number of options a user can select
        )

        embed1 = await self.streaks_global(ctx)
        embed2 = await self.streaks_local(ctx)
        embed3 = await self.streaks_lb(ctx)

        embeds = [embed1, embed2, embed3]

        st = disnake.ui.ActionRow()
        st.append_item(select)

        await ctx.edit_original_message(embed=embed1, components=[st])

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

        tracked = ongoing_stats.find({"tag": {"$in": tracked_members}}).sort("row_triple", -1)
        limit = 25
        results = []
        for player in await tracked.to_list(length=limit):
            thisPlayer = []
            numberOfTriples = player.get("row_triple")
            name = player.get("name")
            if numberOfTriples >= 2:
                thisPlayer.append(name)
                thisPlayer.append(numberOfTriples)
                results.append(thisPlayer)

        ranking = results

        text = ""
        x = 1

        for person in ranking:
            name = person[0]
            name = emoji.get_emoji_regexp().sub(' ', name)
            name = f"{x}. {name}"
            name = name.ljust(15)
            streak = person[1]
            text += translate("perfect_streak", ctx).format(name=name, str=streak)
            x += 1

        if text == "":
            text = translate("no_streaks", ctx)

        board = disnake.Embed(title=f"🔥 {translate('top25_server_streaks', ctx)} 🔥", description=text,
                              color=disnake.Color.blue())
        return board

    async def streaks_global(self, ctx):
        tracked = ongoing_stats.find({"row_triple": {"$gte": 2}}).sort("row_triple", -1)
        limit = 25
        results = []
        for player in await tracked.to_list(length=limit):
            thisPlayer = []
            numberOfTriples = player.get("row_triple")
            name = player.get("name")
            if numberOfTriples >= 2:
                thisPlayer.append(name)
                thisPlayer.append(numberOfTriples)
                results.append(thisPlayer)

        ranking = results

        text = ""
        x = 1

        for person in ranking:
            name = person[0]
            name = emoji.get_emoji_regexp().sub(' ', name)
            name = f"{x}. {name}"
            name = name.ljust(15)
            streak = person[1]
            text += translate("perfect_streak", ctx).format(name=name, str=streak)
            x += 1

        if text == "":
            text = translate("no_streaks", ctx)

        board = disnake.Embed(title=f"🔥 {translate('top25_ongoing_streaks', ctx)} 🔥",
                              description=text,
                              color=disnake.Color.blue())
        return board

    async def streaks_lb(self, ctx):
        tracked = ongoing_stats.find({"highest_streak": {"$gte": 2}}).sort("highest_streak", -1)
        limit = 25
        results = []
        for player in await tracked.to_list(length=limit):
            thisPlayer = []
            numberOfTriples = player.get("highest_streak")
            name = player.get("name")
            if numberOfTriples >= 2:
                thisPlayer.append(name)
                thisPlayer.append(numberOfTriples)
                results.append(thisPlayer)

        ranking = results
        text = ""
        x = 1

        for person in ranking:
            name = person[0]
            name = emoji.get_emoji_regexp().sub(' ', name)
            name = f"{x}. {name}"
            name = name.ljust(15)
            streak = person[1]
            text += translate("perfect_streak", ctx).format(name=name, str=streak)
            x += 1

        if text == "":
            text = translate("no_streaks", ctx)

        board = disnake.Embed(title=f"🔥 {translate('top25_alltime_streaks', ctx)} 🔥",
                              description=text,
                              color=disnake.Color.blue())
        return board

    @commands.slash_command(name="popular", description="View popular tracked players")
    async def popular(self, ctx: disnake.ApplicationCommandInteraction):
        SINGLE_PLAN = await has_single_plan(ctx)
        GUILD_PLAN = await has_guild_plan(ctx)
        TIER, NUM_COMMANDS, MESSAGE = await decrement_usage(ctx, SINGLE_PLAN, GUILD_PLAN)
        if MESSAGE is not None:
            await ctx.response.defer(ephemeral=True)
            return await ctx.send(content=MESSAGE)

        await ctx.response.defer()
        tracked = ongoing_stats.find().sort("popularity", -1)
        playerStats = []
        for document in await tracked.to_list(length=25):
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

        topTen = f"**{translate('popular_bar', ctx)}**\n"
        for x in range (0,25):
            topTen+=f"{playerStats[x][0]} | {playerStats[x][1]} | {playerStats[x][2]}\n"

        board = disnake.Embed(title=f"🔥 {translate('most_popular', ctx)} 🔥 \n",
                              description=topTen,
                              color=disnake.Color.blue())
        await ctx.edit_original_message(embed=board)

    @commands.slash_command(name="breakdown",description="Trophy Breakdown for players tracked.")
    async def breakdown(self, ctx: disnake.ApplicationCommandInteraction):
        SINGLE_PLAN = await has_single_plan(ctx)
        GUILD_PLAN = await has_guild_plan(ctx)
        TIER, NUM_COMMANDS, MESSAGE = await decrement_usage(ctx, SINGLE_PLAN, GUILD_PLAN)
        if MESSAGE is not None:
            await ctx.response.defer(ephemeral=True)
            return await ctx.send(content=MESSAGE)

        await ctx.response.defer()
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

        board = disnake.Embed(title=translate("trophy_breakdown", ctx), description=text,
                              color=disnake.Color.blue())
        await ctx.edit_original_message(embed=board)

    @commands.slash_command(name="legend-popularity", description="Number of legends accounts at EOS over time")
    async def legend_popularity(self, ctx: disnake.ApplicationCommandInteraction):
        SINGLE_PLAN = await has_single_plan(ctx)
        GUILD_PLAN = await has_guild_plan(ctx)
        TIER, NUM_COMMANDS, MESSAGE = await decrement_usage(ctx, SINGLE_PLAN, GUILD_PLAN)
        if MESSAGE is not None:
            await ctx.response.defer(ephemeral=True)
            return await ctx.send(content=MESSAGE)

        await ctx.response.defer()
        y = []
        dates = await coc_client.get_seasons(league_id=29000022)
        for date in dates:
            season_stats = history_db[f"{date}"]
            limit = await season_stats.count_documents(filter={})
            y.append(limit)


        x = []
        for spot in range(0, len(y)):
            x.append(spot)

        x.reverse()
        y.reverse()

        plt.plot(dates, y, color='green', linestyle='dashed', linewidth=2,
                 marker='o', markerfacecolor='blue', markersize=5)
        plt.ylim(min(y) - 100, max(y) + 50000)
        plt.xlim(len(y)+ 1, -1)

        plt.xticks(x, dates, color='blue', rotation=45, fontsize='8',
                   horizontalalignment='right')
        plt.locator_params(axis="x", nbins=10)

        plt.xlabel('Days Ago')
        # naming the y axis
        plt.ylabel('Accounts')
        plt.title(f"Legend Popularity Over Time")
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        file = disnake.File(fp=buf, filename="filename.png")
        pic_channel = await self.bot.fetch_channel(884951195406458900)
        msg = await pic_channel.send(file=file)
        pic = msg.attachments[0].url
        plt.clf()
        plt.close("all")
        await ctx.edit_original_message(content=pic)

    @commands.slash_command(name="eos-finishers", description="Number 1 EOS finishers for every month")
    async def eos_finishers(self, ctx: disnake.ApplicationCommandInteraction):
        SINGLE_PLAN = await has_single_plan(ctx)
        GUILD_PLAN = await has_guild_plan(ctx)
        TIER, NUM_COMMANDS, MESSAGE = await decrement_usage(ctx, SINGLE_PLAN, GUILD_PLAN)
        if MESSAGE is not None:
            await ctx.response.defer(ephemeral=True)
            return await ctx.send(content=MESSAGE)

        await ctx.response.defer()
        text = ""
        oldyear = "2015"
        embed = disnake.Embed(title=translate("#1_finish", ctx),
                              color=disnake.Color.blue())
        dates = await coc_client.get_seasons()
        for date in dates:
            season_stats = history_db[f"{date}"]
            result = await season_stats.find_one({"rank": 1})
            year = date[0:4]
            month = date[5:8]
            month = calendar.month_name[int(month)]
            month = translate(month, ctx)
            month = month.ljust(9)
            if result is not None:
               name = result.get("name")
               trophies = result.get("trophies")
               if year != oldyear:
                   embed.add_field(name=oldyear, value=text, inline=False)
                   text = ""
                   oldyear=year
               text+= f"`{month}` | 🏆{trophies} | \u200e{name}\n"
            else:
                continue

        if text != "":
            embed.add_field(name=f"**{oldyear}**", value=text, inline=False)


        await ctx.edit_original_message(embed=embed)





def setup(bot):
    bot.add_cog(LegendStats(bot))