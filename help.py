
from disnake.ext import commands
import disnake
from utils.helper import ongoing_stats
from looper import coc_client_two
import os
initial_extensions = (
            "check.maincheck",
            "feeds.feeds",
            "leaderboards.leaderboard",
            "stats.mainstats",
            "track.track"  ,
            "on_events",
            "pepe.pepe",
            "help",
            "settings",
            "patreon",
            "check.poster"
        )

class help(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def autocomp_names(self, query: str):
        has = []
        for i in initial_extensions:
            if query in i:
                has.append(i)
        return has

    @commands.command(name='print')
    @commands.is_owner()
    async def print(self, ctx, yes=None):
        cache = coc_client_two.http.cache
        if yes!= None:
            print(cache)
        await ctx.send(len(cache))

    @commands.slash_command(name='reload', guild_ids=[923764211845312533, 810466565744230410, 328997757048324101])
    @commands.guild_permissions(923764211845312533, owner=True)
    @commands.is_owner()
    async def _reload(self,ctx, *, module: str = commands.Param(autocomplete=autocomp_names)):
        """Reloads a module."""
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except:
            await ctx.send('<a:no:862552093324083221> Could not reload module.')
        else:
            await ctx.send('<a:check:861157797134729256> Reloaded module successfully')

    @commands.command(name='leave')
    @commands.is_owner()
    async def leaveg(self, ctx, *, guild_name):
        guild = disnake.utils.get(self.bot.guilds, name=guild_name)  # Get the guild by name
        if guild is None:
            await ctx.send("No guild with that name found.")  # No guild found
            return
        await guild.leave()  # Guild found
        await ctx.send(f"I left: {guild.name}!")


    @commands.command(name="migrate")
    @commands.is_owner()
    async def migrate(self, ctx):

        tracked = ongoing_stats.find()
        limit = await ongoing_stats.count_documents(filter={})
        for document in await tracked.to_list(length=limit):
            servers = document.get("servers")
            if servers is None:
                continue
            tag = document.get("tag")
            if 923764211845312533 in servers:
                await ongoing_stats.update_one({'tag': tag},
                                               {'$pull': {"servers": 923764211845312533}})
        await ctx.send("done")

    @commands.command(name="gitpull")
    @commands.is_owner()
    async def gitpull(self, ctx):
        os.system("cd LegendsTracker2.0")
        os.system("git pull https://github.com/MagicTheDev/LegendsTracker2.0.git")
        await ctx.send("Bot using latest changes.")

    @commands.slash_command(name='invite',
                       description="Invite for bot.")
    async def invite(self, ctx):
        await ctx.send("https://discord.com/api/oauth2/authorize?client_id=825324351016534036&permissions=2147747840&scope=bot%20applications.commands")

    @commands.slash_command(name='server',
                       description="Support server for bot.")
    async def serv(self, ctx):
        await ctx.send(
            "discord.gg/gChZm3XCrS")

    @commands.slash_command(name="help", description="Help command")
    async def help(self, ctx: disnake.ApplicationCommandInteraction):
        select = disnake.ui.Select(
            options=[  # the options in your dropdown
                disnake.SelectOption(label="Setup", value="1"),
                disnake.SelectOption(label="Legends", value="2"),
                disnake.SelectOption(label="Stats", value="3"),
                disnake.SelectOption(label="Settings", value="4"),
                disnake.SelectOption(label="Fun/Other", value="5")
            ],
            placeholder="Choose your option",  # the placeholder text to show when no options have been chosen
            min_values=1,  # the minimum number of options a user must select
            max_values=1,  # the maximum number of options a user can select
        )

        embeds = []

        embed5  = disnake.Embed(title="Quick Start",
                               description=f"Thanks for using me!\n"
                                           f"To get started there are 3 main components to the bot - tracking people & the feed, checking people, and stats.",
                               color=disnake.Color.blue())

        embed5.add_field(name="**Tracking People:**", value=f"There are 3 main ways to track people.\n"
                                           f"> /track #playerTag\n"
                                           f"> /ctrack #clanTag\n"
                                           f"> /country track\n"
                                           f"These 3 will add an individual player, people in a clan, or people on a countries leaderboard, in that order.\n"
                                           f"When it comes to tracking, I split it into 2 parts - \"global\" and  \"server\", when you track someone on your server, it is adding it "
                                           f"to server tracking, but also global tracking if they havent been already. Global tracking is just the global pool of players, so you can check someones "
                                           f"stats even if you dont want them in your feed or tracked on your server.\n"
                                           f"Of course any tracked players you can view in your feed if you set it up. With `/feed set`. Make sure it has correct perms.", inline=False)
        embed5.add_field(name="**Checking People:**", value=f"So to check people, we have the aptly named /check commands.\n"
                                           f"> /check search\n"
                                           f"> /check user\n"
                                           f"> /check clan\n"
                                           f"> /quick_check\n"
                                           f"Check search is the most powerful command on the bot. No more looking for a players tag to look them up (although you can). Just type in their name & let "
                                           f"the autocomplete do the rest\n"
                                           f"Check user uses any accounts linked to you, this is just a convenience feature, if you have an account linked to clash perk or sidekick it will show.\n"
                                           f"Check clan will give a leaderboard view of legends stats in a clan. And lastly quick_check allows you to save players to your profile for quick checking, and also "
                                           f"allows you to use the /daily_report command.", inline=False)
        embed5.add_field(name="**Stats**", value=f"There are a plethora of stats available, checking the command list is best.\n"
                                           f"However among the most popular are:\n"
                                           f"> /poster #playerTag\n"
                                           f"> /country leaderboards\n"
                                           f"> /streak\n"
                                           f"> /top", inline=False)
        embed5.set_footer(text="Use dropdown below to navigate.")
        embeds.append(embed5)

        embed = disnake.Embed(title="Legends Tracker",
                              description="Legends Commands",
                              color=disnake.Color.blue())

        embed.add_field(name=f"**/check search**",
                        value="Check/Search a person's legends hits & defenses for today.\nSupports searching by name or player tag\n"
                              "- Uses autocomplete to return matches as you type"
                              "\nExamples:\n"
                              "-/check search magic\n"
                              "- /check search #PGY2YRQ\n",
                        inline=False)

        embed.add_field(name=f"**/check user**",
                        value="Check/Search a person's legends hits & defenses for today.",
                        inline=False)

        embed.add_field(name=f"**/check clan**",
                        value="Leaderboard results of how everyone in a clan is doing.\n"
                              "If players are missing, lets you globally track the missing ones.",
                        inline=False)

        embed.add_field(name=f"**/quick_check**",
                        value="Save up to 25 players to your profile to easily check them with **no** hassle.",
                        inline=False)

        embed.add_field(name=f"**/daily_report**",
                        value="If opted in, get a daily end of day report of the players you have added to `/quick_check`.",
                        inline=False)

        embed.add_field(name=f"**/track add [#playerTag]**",
                        value="Use this command to start tracking statistics on an account.",
                        inline=False)
        embed.add_field(name=f"**/track remove [#playerTag]**",
                        value="Use this command to remove an account from server tracking.",
                        inline=False)
        embed.add_field(name=f"**/ctrack add [#clanTag]**",
                        value="Manage Guild Required. Use this command to link & add a clan's accounts to your server.",
                        inline=False)
        embed.add_field(name=f"**/ctrack remove [#clanTag]**",
                        value="Manage Guild Required. Use this command to remove a clan's accounts to your server.",
                        inline=False)
        embed.add_field(name=f"**/ctrack sync**",
                        value="Manage Guild Required. Use this command to sync or add to your feed from your server's linked clans..",
                        inline=False)
        embed.add_field(name=f"**/ctrack list**",
                        value="See server's linked clans.",
                        inline=False)

        embed.add_field(name="**/tracked_list [clans or players]**",
                        value="List of clans found in your feed or players linked in your feed.",
                        inline=False)
        embed.add_field(name=f"**/country track**",
                        value="Add the top # of players from a country leaderboard to your feed.",
                        inline=False)

        embeds.append(embed)

        embed2 = disnake.Embed(title="Legends Tracker",
                               description="Stats Commands",
                               color=disnake.Color.blue())

        embed2.add_field(name=f"**/poster**",
                         value="Visual poster containing season legends stats.",
                         inline=False)
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
        embed2.add_field(name=f"**/country leaderboards**",
                         value="Top 200 Leaderboard of a country.",
                         inline=False)
        embeds.append(embed2)

        embed3 = disnake.Embed(title="Legends Tracker",
                               description="Settings Commands",
                               color=disnake.Color.blue())
        embed3.add_field(name=f"**/feed set**",
                         value="Manage Guild Required.*\nCreates a feed in the channel you run the command.",
                         inline=False)
        embed3.add_field(name=f"**/feed remove**",
                         value="Manage Guild Required.*\nRemove the channel for legends feed",
                         inline=False)
        embeds.append(embed3)

        embed4 = disnake.Embed(title="Legends Tracker",
                               description="Other Commands",
                               color=disnake.Color.blue())

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

        dropdown = disnake.ui.ActionRow()
        dropdown.append_item(select)

        await ctx.send(embed=embed5, components=[dropdown])
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

            if res.author.id != ctx.author.id:
                await res.send(content="You must run the command to interact with components.", ephemeral=True)
                continue

            # print(res.selected_options)
            await res.response.edit_message(embed=embeds[int(res.values[0]) - 1])




def setup(bot: commands.Bot):
    bot.add_cog(help(bot))
