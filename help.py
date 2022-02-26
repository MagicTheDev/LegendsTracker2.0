
from discord.ext import commands
import discord
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, wait_for_component
from discord_slash import cog_ext
from helper import ongoing_stats, server_db

class help(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="check")
    async def check(self, ctx):
        await ctx.send("All commands have been moved to slash commands. Start with a `/` in the chat to view them.\n"
                       "Slash commands not showing up? Reinvite me.\nNeed Help? Join the support server - discord.gg/gChZm3XCrS\nhttps://discord.com/api/oauth2/authorize?client_id=825324351016534036&permissions=2147747840&scope=bot%20applications.commands")

    @commands.command(name='leave')
    @commands.is_owner()
    async def leaveg(self, ctx, *, guild_name):
        guild = discord.utils.get(self.bot.guilds, name=guild_name)  # Get the guild by name
        if guild is None:
            await ctx.send("No guild with that name found.")  # No guild found
            return
        await guild.leave()  # Guild found
        await ctx.send(f"I left: {guild.name}!")


    @commands.command(name="numbers")
    @commands.is_owner()
    async def numbers(self, ctx):
        tracked = ongoing_stats.find()
        limit = await ongoing_stats.count_documents(filter={})
        serverList = []
        count = []
        for document in await tracked.to_list(length=limit):

            servers = document.get("servers")
            if servers == None:
                print(document.get("tag"))
                continue

            for server in servers:
                if server not in serverList:
                    serverList.append(server)
                    count.append(1)
                else:
                    ind = serverList.index(server)
                    count[ind] += 1

        topTen = ""
        for x in range(0, len(serverList)):
            try:
                guild = await self.bot.fetch_guild(serverList[x])
            except:
                continue
            topTen += f"{guild.name} | {count[x]}\n"

        board = discord.Embed(title="**Numbers Tracked by Server**",
                              description=topTen,
                              color=discord.Color.blue())
        await ctx.send(embed=board)


    @commands.command(name="migrate")
    @commands.is_owner()
    async def migrate(self, ctx):
        updated = ""
        tracked = server_db.find()
        limit = await server_db.count_documents(filter={})
        # print(f"Loop 1 size {limit}")
        for document in await tracked.to_list(length=limit):
            channel = document.get("channel_id")
            if channel == None:
                continue
            channel = await self.bot.fetch_channel(channel)

            print(channel.name)
            print(channel.id)



    @cog_ext.cog_slash(name='invite',
                       description="Invite for bot.")
    async def invite(self, ctx):
        await ctx.send("https://discord.com/api/oauth2/authorize?client_id=825324351016534036&permissions=2147747840&scope=bot%20applications.commands")

    @cog_ext.cog_slash(name='server',
                       description="Support server for bot.")
    async def serv(self, ctx):
        await ctx.send(
            "discord.gg/gChZm3XCrS")

    @cog_ext.cog_slash(name="help", description="Help command")
    async def help(self, ctx):
        select = create_select(
            options=[  # the options in your dropdown
                create_select_option("Setup", value="1"),
                create_select_option("Legends", value="2"),
                create_select_option("Stats", value="3"),
                create_select_option("Settings", value="4"),
                create_select_option("Fun/Other", value="5")
            ],
            placeholder="Choose your option",  # the placeholder text to show when no options have been chosen
            min_values=1,  # the minimum number of options a user must select
            max_values=1,  # the maximum number of options a user can select
        )

        embeds = []

        embed5 = discord.Embed(title="Legends Tracker",
                               description=f"**Quick Setup:**To set up a attack/defense feed use `/feed set #channel`\n"
                                           f"To start tracking a player & add them to your server use `/track add #playerTag`\n"
                                           f"To start tracking a player & add them to your server use `/track remove #playerTag`\n"
                                           f"For other commands & help check out `/help`\n"
                                           "**NOTE:** Players have to be tracked before you can view stats on them, after that stats will start to show as they are collected.",
                               color=discord.Color.blue())

        embeds.append(embed5)

        embed = discord.Embed(title="Legends Tracker",
                              description="Legends Commands",
                              color=discord.Color.blue())

        embed.add_field(name=f"**/check**",
                        value="__\nCheck/Search a person's legends hits & defenses for today.\n Supports searching by player tag, discord ID, or by name."
                              "\nExamples:\n"
                              "- /check magic\n"
                              f"- /check {ctx.author.mention}\n"
                              "- /check #PGY2YRQ\n",
                        inline=False)

        embed.add_field(name=f"**/quick_check**",
                        value="Save up to 25 players to your profile to easily check them with **no** hassle.",
                        inline=False)

        embed.add_field(name=f"**/track add [#playerTag]**",
                        value="Use this command to start tracking statistics on an account.",
                        inline=False)
        embed.add_field(name=f"**/track remove [#playerTag]**",
                        value="Use this command to remove an account from server tracking.",
                        inline=False)
        embed.add_field(name=f"**/ctrack add [#clanTag]**",
                        value="Manage Guild Required. Use this command to add a clan's accounts to your server.",
                        inline=False)
        embed.add_field(name=f"**/ctrack remove [#clanTag]**",
                        value="Manage Guild Required. Use this command to remove a clan's accounts to your server.",
                        inline=False)

        embed.add_field(name="**/tracked_list [clans or players]**",
                        value="List of clans or players linked in your feed.",
                        inline=False)

        embeds.append(embed)

        embed2 = discord.Embed(title="Legends Tracker",
                               description="Stats Commands",
                               color=discord.Color.blue())

        embed2.add_field(name=f"**/top**",
                         value="Use this command to get top hitters & defenders tracked.",
                         inline=False)
        embed2.add_field(name=f"**/streak**",
                         value="Use this command to get current 3 star streak stats.",
                         inline=False)
        embed2.add_field(name=f"**/stats**",
                         value="Bot statistics (Uptime, accounts tracked, etc)",
                         inline=False)
        embed2.add_field(name=f"**/breakdown**",
                         value="Number of players tracked at each trophy range",
                         inline=False)
        embed2.add_field(name=f"**/popular**",
                         value="Popularly tracked players across servers.",
                         inline=False)
        embed2.add_field(name=f"**/history [playerTag]**",
                         value="Rankings & Trophies for end of previous seasons.",
                         inline=False)
        embed2.add_field(name=f"**/leaderboard**",
                         value="Display server leaderboard of tracked players.",
                         inline=False)
        embed2.add_field(name=f"**/country_leaderboards**",
                         value="Top 200 Leaderboard of a country.",
                         inline=False)
        embeds.append(embed2)

        embed3 = discord.Embed(title="Legends Tracker",
                               description="Settings Commands",
                               color=discord.Color.blue())
        embed3.add_field(name=f"**/feed set [channel]**",
                         value="Manage Guild Required.*\nSet the channel where for updating legends feed",
                         inline=False)
        embed3.add_field(name=f"**/feed remove**",
                         value="Manage Guild Required.*\nRemove the channel for legends feed",
                         inline=False)
        embeds.append(embed3)

        embed4 = discord.Embed(title="Legends Tracker",
                               description="Other Commands",
                               color=discord.Color.blue())

        embed4.add_field(name=f"**/link**",
                         value="Link a player to your discord account.",
                         inline=False)

        embed4.add_field(name=f"**/pepe [text]**",
                         value="Use this command to create a pepe holding a sign with the text.",
                         inline=False)

        embed4.add_field(name=f"**/invite**",
                         value="Link to invite bot.",
                         inline=False)

        embed4.add_field(name=f"**/server**",
                         value="Link to support server.",
                         inline=False)

        embeds.append(embed4)

        dropdown = create_actionrow(select)

        msg = await ctx.send(embed=embed5, components=[dropdown])

        while True:
            try:
                res = await wait_for_component(self.bot, components=select, messages=msg, timeout=600)
            except:
                await msg.edit(components=None)
                break

            if res.author_id != ctx.author.id:
                await res.send(content="You must run the command to interact with components.", hidden=True)
                continue

            await res.edit_origin()
            # print(res.selected_options)
            await msg.edit(embed=embeds[int(res.selected_options[0]) - 1])




def setup(bot: commands.Bot):
    bot.add_cog(help(bot))