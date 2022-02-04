from discord.ext import commands
import discord


class bot_settings(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.command(name='setfeed')
    @commands.has_permissions(manage_guild=True)
    async def setfeed(self, ctx, *, extra):
        results = await settings.find_one({"server_id": ctx.guild.id})

        if results == None:
            await settings.insert_one({"server_id": ctx.guild.id, "channel_id": None, "feedlimit": 5000})
        
        ex = extra.lower()
        if ex == "none" :          
          await settings.update_one({"server_id": ctx.guild.id}, {'$set': {"channel_id": None}})
          embed = discord.Embed(description=f"Feed channel removed.",
                                color=discord.Color.green())
          return await ctx.send(embed=embed)

        if (extra.startswith('<#') and extra.endswith('>')):
            extra = extra[2:len(extra) - 1]
        try:
            extra = int(extra)
        except:
            pass
        
        try:
          extra = await self.bot.fetch_channel(extra)
          c = extra   
          g = ctx.guild
          r = await g.fetch_member(825324351016534036)
          perms = c.permissions_for(r)      
          send_msg = perms.send_messages
          external_emoji = perms.use_external_emojis
          if send_msg == False or external_emoji == False:
            embed = discord.Embed(description=f"Feed channel canceled. Missing Permissions in that channel.\nMust have `Send Messages` and `Use External Emojis` in the feed channel.\n `do setfeed none` to remove feed.",
                                    color=discord.Color.red())
            return await ctx.send(embed=embed)
        except:
          embed = discord.Embed(description=f"Invalid channel or Missing Access to view channel.\n`do setfeed none` to remove feed.",
                                    color=discord.Color.red())
          return await ctx.send(embed=embed)             

        channel = extra.id

        await settings.update_one({"server_id": ctx.guild.id}, {'$set': {"channel_id": channel}})

        embed = discord.Embed(description=f"{extra.mention} set as feed channel.\nEnsure I have permission to send messages there.\nView current feed channel with `do stats`.",
                              color=discord.Color.green())
        return await ctx.send(embed=embed)

    @commands.command(name='trophylimit')
    @commands.has_permissions(manage_guild=True)
    async def trophyLimit(self, ctx, *, extra):
        results = await settings.find_one({"server_id": ctx.guild.id})

        if results == None:
            embed = discord.Embed(
                description="Sorry this server does not have a legends feed. Those with Manage Guild Perms can add one with **do setfeed #channel**.",
                color=discord.Color.red())
            return await ctx.send(embed=embed)

        fchannel = results.get("channel_id")
        if fchannel == None:
            embed = discord.Embed(
                description="Sorry this server does not have a legends feed. Those with Manage Guild Perms can add one with **do setfeed #channel**.",
                color=discord.Color.red())
            return await ctx.send(embed=embed)

        try:
            extra = int(extra)
        except:
            return await ctx.send("Limit must be a valid integer.")

        results = await settings.find_one({"server_id": ctx.guild.id})
        if results == None:
            await settings.insert_one({"server_id": ctx.guild.id, "channel_id": None, "feedlimit": 5000})
        else:
            await settings.update_one({"server": ctx.guild.id}, {'$set': {"feedlimit": extra}})


        embed = discord.Embed(description=f"Only trophies above {extra} show in the feed channel now.\nView current trophylimit with `do stats`.",
                              color=discord.Color.green())
        return await ctx.send(embed=embed)

    @commands.command(name='leave')
    @commands.is_owner()
    async def leaveg(self, ctx, *, guild_name):
        guild = discord.utils.get(self.bot.guilds, name=guild_name)  # Get the guild by name
        if guild is None:
            await ctx.send("No guild with that name found.")  # No guild found
            return
        await guild.leave()  # Guild found
        await ctx.send(f"I left: {guild.name}!")

    @commands.command(name='servers')
    @commands.is_owner()
    async def servers(self, ctx):
        text = ""
        guilds = self.bot.guilds
        for guild in guilds:
            id =guild.member_count
            #owner = await self.bot.fetch_user(id)
            text += guild.name +f" | {id} members\n"

        embed = discord.Embed(description=text,
                              color=discord.Color.green())


        await ctx.send(embed =embed)



    @commands.command(name="setprefix")
    @commands.check_any(commands.has_permissions(manage_guild=True))
    async def setprefix(self, ctx, prefix=None):
        if prefix is None:
            return await ctx.reply("Provide a prefix to switch to",
                                   mention_author=False)

        try:
            results = await server.find_one({"server": ctx.guild.id})
            old_prefix = results.get("prefix")
            if prefix == "do":
                prefix = "do "
        except:
            old_prefix = "do "
            await server.insert_one({
                "server": ctx.guild.id,
                "prefix": "do ",
            })


        await server.update_one({"server": ctx.guild.id}, {'$set': {"prefix": prefix}})

        await ctx.reply(f"Prefix switched from {old_prefix} to {prefix}",
                        mention_author=False)


    '''
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingPermissions):
            await ctx.send("You are missing permission(s) to run this command.")
    '''

    @setfeed.error
    @trophyLimit.error
    async def set_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            message = "You are missing the required permissions to run this command! Manage Guild Required."
            await ctx.send(message)

    

      
      






def setup(bot: commands.Bot):
    bot.add_cog(bot_settings(bot))