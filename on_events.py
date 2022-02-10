from discord.ext import commands
import discord

from helper import server_db



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
                    "tracked_members": [],
                    "channel_id": None
                })

    @commands.Cog.listener()
    async def on_application_command(self,ctx):
        channel = self.bot.get_channel(936069341693231155)
        server = ctx.guild.name
        user = ctx.author
        command = ctx.command.qualified_name
        embed = discord.Embed(description=f"**{command}** \nused by {user.mention} [{user.name}] in {server} server",
                              color=discord.Color.blue())
        embed.set_thumbnail(url=user.avatar.url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        try:
            channel = guild.text_channels[0]
            embed = discord.Embed(title="Hello " + guild.name + "!", description="Thanks for inviting me!\n"
                                                                                 f"**Quick Setup:**To set up a attack/defense feed use `/setfeed #channel`\n"
                                                                                 f"To start tracking a player & add them to your server use `/track add #playerTag`\n"
                                                                                 f"To start tracking a player & add them to your server use `/track remove #playerTag`\n"
                                       f"For other commands & help check out `/help`\n"
                                       "**NOTE:** Players have to be tracked before you can view stats on them, after that stats will start to show as they are collected."
                                                                                 "If any questions concerns or problems, join the support server: https://discord.gg/Z96S8Gg2Uv")
            await channel.send(embed=embed)
        except:
            pass
        results = await server_db.find_one({"server": guild.id})
        if results is None:
            await server_db.insert_one({
                "server": guild.id,
                "tracked_members": [],
                "channel_id" : None
            })
        channel = self.bot.get_channel(937519135607373874)
        await channel.send(f"Just joined {guild.name}")

    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        await server_db.find_one_and_delete({'server_id': guild.id})




def setup(bot: commands.Bot):
    bot.add_cog(Bot_Events(bot))