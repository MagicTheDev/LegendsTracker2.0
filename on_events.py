from disnake.ext import commands
import disnake
from utils.helper import server_db

class Bot_Events(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        print('We have logged in')
        len_g = len(self.bot.guilds)
        await self.bot.change_presence(
            activity=disnake.Activity(name=f'{len_g} servers', type=3))  # type 3 watching type#1 - playing
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
        command = ctx.data.name
        embed = disnake.Embed(description=f"**{command} {ctx.filled_options}** \nused by {user.mention} [{user.name}] in {server} server",
                              color=disnake.Color.blue())
        #embed.set_thumbnail(url=user.avatar.url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        try:
            channel = guild.text_channels[0]
            embed = disnake.Embed(title="Thanks for inviting me!",
                               description=f"**Quick Setup:**\n"
                                           f"**To set up a attack/defense feed use `/feed set`\n"
                                           f"> Run the command in the channel (or thread) you want the bot to post in."
                                           f"> Must have `Manage Webhooks` Permission to do so."
                                           f"To track a player & add them to your server use `/track add #playerTag`\n"
                                           f"To add entire clans - use `/ctrack add #playerTag`\n"
                                           f"Checking a player's stats has never been easier with `/check search`"
                                           f"For other commands & help check out `/help`\n"
                                           "**NOTE:** Players have to be tracked before you can view stats on them, after that stats will start to show as they are collected.",
                               color=disnake.Color.blue())
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
        await channel.send(f"Just joined {guild.name}, {guild.member_count} members")
        len_g = len(self.bot.guilds)
        await self.bot.change_presence(
            activity=disnake.Activity(name=f'{len_g} servers', type=3))  # type 3 watching type#1 - playing
        channel = self.bot.get_channel(937528755973419048)
        await channel.edit(name=f"LegendsBot: {len_g} Servers")

    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        await server_db.find_one_and_delete({'server_id': guild.id})
        channel = self.bot.get_channel(937519135607373874)
        await channel.send(f"Just left {guild.name}, {guild.member_count} members")
        len_g = len(self.bot.guilds)
        await self.bot.change_presence(
            activity=disnake.Activity(name=f'{len_g} servers', type=3))  # type 3 watching type#1 - playing
        channel = self.bot.get_channel(937528755973419048)
        await channel.edit(name=f"LegendsBot: {len_g} Servers")



def setup(bot: commands.Bot):
    bot.add_cog(Bot_Events(bot))