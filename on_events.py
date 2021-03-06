from disnake.ext import commands
import disnake
from utils.helper import server_db, MissingGuildPlan
import traceback

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
        if ctx.guild is None:
            server = "None"
        else:
            server = ctx.guild.name
        user = ctx.author
        command = ctx.data.name
        embed = disnake.Embed(description=f"**{command} {ctx.filled_options}** \nused by {user.mention} [{user.name}] in {server} server",
                              color=disnake.Color.blue())
        embed.set_thumbnail(url=user.display_avatar.url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        try:
            channel = guild.text_channels[0]
            embed = disnake.Embed(title="Thanks for inviting me!",
                               description="Run /quick_start for quick setup guide.",
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


    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx: disnake.ApplicationCommandInteraction, error: disnake.ext.commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            embed = disnake.Embed(
                description=f"You are missing permissions to use `/{ctx.application_command.qualified_name}`.\n"
                            f"**Permissions Required**: `{' '.join(error.missing_permissions)}`",
                color=disnake.Color.red())
            return await ctx.send(embed=embed)
        elif isinstance(error, MissingGuildPlan):
            embed = disnake.Embed(
                description=f"**This command requires a [guild subscription](https://www.patreon.com/magicbots).**",
                color=disnake.Color.red())
            return await ctx.send(embed=embed)
        elif isinstance(error, commands.MessageNotFound) or isinstance(error, disnake.NotFound):
            pass
        else:
            if ctx.guild is None:
                embed = disnake.Embed(
                    description=f"This bot no longer allows commands in DM, please use commands in a server.",
                    color=disnake.Color.red())
                await ctx.send(embed=embed, ephemeral=True)
            else:
                e = str(error)[0:3000]
                if "404 Not Found" in e:
                    return
                embed2 = disnake.Embed(
                    description=f"Unhandled Error: {str(error)[0:3000]}",
                    color=disnake.Color.red())
                channel = await self.bot.fetch_channel(989919520405725264)
                await channel.send(content=f"`/{ctx.application_command.qualified_name} {ctx.filled_options}`", embeds=[embed2])




def setup(bot: commands.Bot):
    bot.add_cog(Bot_Events(bot))
