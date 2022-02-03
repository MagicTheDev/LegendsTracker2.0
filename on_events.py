from discord.ext import commands
import discord

from helper import ongoing_stats, server_db, settings_db



class Bot_Events(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('We have logged in')
        await self.bot.change_presence(
            activity=discord.Activity(name='you triple 😉', type=3))  # type 3 watching type#1 - playing
        for g in self.bot.guilds:
            results = await server_db.find_one({"server": g.id})
            if results is None:
                await server_db.insert_one({
                    "server": g.id,
                    "prefix": "do ",
                })

    @commands.Cog.listener()
    async def on_command(self,ctx):
        pass
        channel = self.bot.get_channel(936069341693231155)
        server = ctx.guild.name
        user = ctx.author
        command = ctx.message.content
        embed = discord.Embed(description=f"**{command}** \nused by {user.mention} [{user.name}] in {server} server",
                              color=discord.Color.blue())
        embed.set_thumbnail(url=user.avatar_url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        try:
            channel = guild.text_channels[0]
            embed = discord.Embed(title="Hello " + guild.name + "!", description="Thanks for inviting me!\n"
                                                                                 "To set up a attack/defense feed use `do setfeed #channel`\n"
                                                                                 "To start tracking a player use `do track #playerTag`\n"
                                                                                 "To add a player to your feed use `do feed #playerTag` (this starts tracking if not already, to save you a step of tracking.)\n"
                                                                                 "For other commands & help check out `do help`\n"
                                                                                 "If any questions concerns or problems, join the support server: https://discord.gg/Z96S8Gg2Uv")
            await channel.send(embed=embed)
        except:
            pass
        results = await server_db.find_one({"server": guild.id})
        if results is None:
            await server_db.insert_one({
                "server": guild.id,
                "prefix": "do ",
            })
        channel = self.bot.get_channel(937519135607373874)
        await channel.send(f"Just joined {guild.name}")

    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        guilds = self.bot.guilds

        guild_ids = []
        for guild in guilds:
            guild_ids.append(guild.id)

        removed_channels = []
        tracked = settings_db.find({})
        limit = await settings_db.count_documents(filter={})
        for document in await tracked.to_list(length=limit):
            server = document.get("server_id")
            if server not in guild_ids:
                await ongoing_stats.find_one_and_delete({'server_id': server})

        tracked = ongoing_stats.find({})
        limit = await ongoing_stats.count_documents(filter={})
        for document in await tracked.to_list(length=limit):
            servers = document.get("servers")
            tag = document.get("tag")
            for s in servers:
                if s in removed_channels:
                    await ongoing_stats.update_one({'tag': f"{tag}"},
                                                   {'$pull': {'servers': s}})

    @commands.Cog.listener()
    async def on_message(self,message):
        ping = "825324351016534036"
        if ping in message.content:
            results = await server_db.find_one({"server": message.guild.id})
            try:
                prefix = results.get("prefix")
            except:
                prefix = "do "
            await message.channel.send(f"Hello! My prefix is `{prefix}` (i.e `{prefix}help`)")

        await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_message_edit(self,before, after):
        try:
            await self.bot.process_commands(after)  # Bot will attempt to process the new edited command
        except:
            pass



def setup(bot: commands.Bot):
    bot.add_cog(Bot_Events(bot))