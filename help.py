
from discord.ext import commands
import discord


import inspect

class help(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='help')
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
        prefix = ctx.prefix
        embeds = []

        embed5 = discord.Embed(title="Legends Tracker",
                              description=f"**Quick Setup:**To set up a attack/defense feed use `{prefix}setfeed #channel`\n"
                                          f"To start tracking a player use `{prefix}track #playerTag`\n"
                                          f"To add a player to your server feed use `{prefix}feed #playerTag` (this also starts tracking if not already, to save you a step of tracking.)\n"
                                          f"For other commands & help check out `{prefix}help`\n"
                                          "**NOTE:** Players have to be tracked before you can view stats on them, after that stats will start to show as they are collected.",
                              color=discord.Color.blue())


        embeds.append(embed5)

        embed = discord.Embed(title="Legends Tracker",
                              description="Legends Commands",
                              color=discord.Color.blue())

        embed.add_field(name=f"**{prefix} check**",
                        value="__\nCheck/Search a person's legends hits & defenses for today.\n Supports searching by player tag, discord ID, or by name."
                              "\nExamples:\n"
                              "- do check magic\n"
                              "- do check <@706149153431879760>\n"
                              "- do check #PGY2YRQ\n",
                        inline=False)

        embed.add_field(name=f"**{prefix} track [#playerTag]**",
                        value="Use this command to start tracking statistics on an account.",
                        inline=False)
        embed.add_field(name=f"**{prefix} feed [#playerTag]**",
                        value="Use this command to add an account to the live legends feed. Starts tracking if not already.",
                        inline=False)
        embed.add_field(name=f"**{prefix} cfeed [#clanTag]**",
                        value="Use this command to add a clan's accounts to the live legends feed.\nCan get quite spammy in your feed channel if you add too many 💀",
                        inline=False)
        embed.add_field(name=f"**{prefix} feed remove [playerTag]**",
                         value="Remove a player from your legends feed.",
                         inline=False)

        embed.add_field(name=f"**{prefix} cfeed remove [#clanTag]**",
                        value="Manage Guild Required. Use this command to remove a clan's accounts from the live legends feed. Quicker way to remove bulk accounts.",
                        inline=False)
        '''
        embed.add_field(name="~~**do clanlist**~~ | Coming Soon.",
                        value="~~List of clans & number of accounts linked in your feed.~~",
                        inline=False)

        embed.add_field(name="~~**do playerlist**~~ | Coming Soon.",
                        value="~~List of players linked in your feed.~~",
                        inline=False)
        '''
        embeds.append(embed)

        embed2 = discord.Embed(title="Legends Tracker",
                              description="Stats Commands",
                              color=discord.Color.blue())

        embed2.add_field(name=f"**{prefix} best**",
                        value="Use this command to get top hitters & defenders tracked.",
                        inline=False)
        embed2.add_field(name=f"**{prefix} streak**",
                        value="Use this command to get current 3 star streaks.",
                        inline=False)
        embed2.add_field(name=f"**{prefix} stats**",
                         value="Bot statistics (Uptime, accounts tracked, etc)",
                         inline=False)
        embed2.add_field(name=f"**{prefix} lstats**",
                         value="Average offensive & defensive rates at each trophy range.",
                         inline=False)
        embed2.add_field(name=f"**{prefix} breakdown**",
                         value="Number of players tracked at each trophy range",
                         inline=False)
        embed2.add_field(name=f"**{prefix} popular**",
                         value="Popularly tracked players (in server feed) across servers.",
                         inline=False)
        embed2.add_field(name=f"**{prefix} history [playerTag]**",
                         value="Rankings & Trophies for end of previous seasons.",
                         inline=False)
        embeds.append(embed2)

        embed3 = discord.Embed(title="Legends Tracker",
                               description="Settings Commands",
                               color=discord.Color.blue())
        embed3.add_field(name=f"**{prefix} setfeed [channel]**",
                         value="Manage Guild Required\nSet the channel where for updating legends feed, *do setfeed None* to remove.",
                         inline=False)
        embed3.add_field(name=f"**{prefix} trophylimit [integer]**",
                         value="Manage Guild Required\nSet a lower limit for updates that show in your feed (helpful if a lot tracked in feed).",
                         inline=False)
        embed3.add_field(name=f"**{prefix}setprefix NEWPREFIX**",
                          value="Set a new prefix for the bot.",
                          inline=False)
        embeds.append(embed3)

        embed4 = discord.Embed(title="Legends Tracker",
                               description="Other Commands",
                               color=discord.Color.blue())

        embed4.add_field(name=f"**{prefix} link**",
                        value="Link a player to your discord account.",
                        inline=False)

        embed4.add_field(name=f"**{prefix} pepe text**",
                        value="Use this command to create a pepe holding a sign with the text.",
                        inline=False)

        if ctx.guild.id == 328997757048324101:
            embed4.add_field(name="**{prefix} pfp {text here}**",
                             value="Use this command to create a usa fam profile pic.",
                             inline=False)


        embed4.add_field(name=f"**{prefix} invite**",
                         value="Link to invite bot.",
                         inline=False)

        embed4.add_field(name=f"**{prefix} server**",
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
            #print(res.selected_options)
            await msg.edit(embed=embeds[int(res.selected_options[0])-1])


    @commands.command(name="invite")
    async def invite(self, ctx):
        await ctx.send("https://discord.com/api/oauth2/authorize?client_id=825324351016534036&permissions=2147747840&scope=bot%20applications.commands")


    @commands.command(name="eval")
    @commands.is_owner()
    async def eval(self, ctx, *, code):
        result = eval(code)
        await ctx.send(f"```{result}```")

    @commands.command(name="notice")
    @commands.is_owner()
    async def stuff(self, ctx, g):
      guild = self.bot.get_guild(int(g))
      print(guild.text_channels)
      for x in range (0, len(guild.text_channels)):
        try:
          channel = guild.text_channels[x]
          await channel.send("Sorry I did not have access to your legends feed, feed was removed. Message `Magic Jr.#6969` if you have any questions.")
          return
        except:
          continue

    @commands.command(name="server")
    async def serv(self, ctx):
        await ctx.send(
            "discord.gg/Z96S8Gg2Uv")









def setup(bot: commands.Bot):
    bot.add_cog(help(bot))