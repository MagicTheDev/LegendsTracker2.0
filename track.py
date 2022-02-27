from discord.ext import commands
from helper import getPlayer, getClan, ongoing_stats, server_db, addLegendsPlayer_SERVER, addLegendsPlayer_GLOBAL, removeLegendsPlayer_SERVER
import discord
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

### SERVER MODEL###
"""
server_db.insert_one({
    "server": guild.id,
    "tracked_members": [],
})
"""

class track(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_subcommand(base="track", name="add",
                            description="Add legends tracking for a player.",
                            options=[
                                create_option(
                                    name="player_tag",
                                    description="Tag to track",
                                    option_type=3,
                                    required=True,
                                )]
                            )
    async def track_add(self,ctx, player_tag):
        # pull player from tag, check if valid player or in legends
        player = await getPlayer(player_tag)
        valid = await self.valid_player_check(ctx=ctx, player=player)
        if not valid:
            return

        is_server_tracked = await self.check_server_tracked(player, ctx.guild.id)
        is_global_tracked = await self.check_global_tracked(player)

        results = await server_db.find_one({"server": ctx.guild.id})
        tracked_members = results.get("tracked_members")
        feed = results.get("channel_id")

        is_full = (len(tracked_members) > 500) and (feed is not None)

        if len(tracked_members) > 500 and feed is not None:
            embed = discord.Embed(
                description="Sorry this command cannot be used while you have more than 500 people tracked and have feed enabled.\n"
                            "Please clear some members with `/clear_under`, sync members with `/clan_track sync`, or remove individual accounts with `/track remove`",
                color=discord.Color.red())
            return await ctx.send(embed=embed)

        if is_global_tracked and is_server_tracked:
            embed = discord.Embed(description=f"{player.name} is already globally & server tracked.",
                                  color=discord.Color.green())
            return await ctx.send(embed=embed)
        elif is_global_tracked and not is_server_tracked:
            if is_full:
                embed = discord.Embed(description=f"**This player is already globally tracked**\nHowever, cannot server track this player. Feed is full - has 500 players.\n"
                                                  f"Please clear some members with `/clear_under`, sync members with `/clan_track sync`, or remove individual accounts with `/track remove`",
                                      color=discord.Color.from_rgb(255,255,0))
                return await ctx.send(embed=embed)
            else:
                embed = discord.Embed(description=f"{player.name} added to server tracking.",
                                      color=discord.Color.green())
                await addLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)

                return await ctx.send(embed=embed)
        else:
            if is_full:
                embed = discord.Embed(description=f"**Player added for global tracking.**\n However, cannot server track this player. Feed is full - has 500 players.\n"
                                                  f"Please clear some members with `/clear_under`, sync members with `/clan_track sync`, or remove individual accounts with `/track remove`",
                                      color=discord.Color.from_rgb(255,255,0))
                await ctx.send(embed=embed)

            clan_name = "No Clan"
            if player.clan != None:
                clan_name = player.clan.name


            await addLegendsPlayer_GLOBAL(player=player, clan_name=clan_name)
            if not is_full:
                await addLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)

            embed = discord.Embed(
                description=f"[{player.name}]({player.share_link}) | {clan_name} was added for legends tracking.",
                color=discord.Color.green())
            await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(base="track", name="remove",
                            description="Remove server legends tracking for a player.",
                            options=[
                                create_option(
                                    name="player_tag",
                                    description="Tag to remove",
                                    option_type=3,
                                    required=True,
                                )]
                            )
    async def track_remove(self,ctx, player_tag):
        player = await getPlayer(player_tag)
        if player is None:
            embed = discord.Embed(description=f"`{player_tag}` not a valid player tag. Check the spelling or use a different tag.",
                                  color=discord.Color.red())
            return await ctx.send(embed=embed)

        is_server_tracked = await self.check_server_tracked(player=player, server_id=ctx.guild.id)
        if not is_server_tracked:
            embed = discord.Embed(description="This player is not server tracked at this time.",
                                  color=discord.Color.red())
            return await ctx.send(embed=embed)

        await removeLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)
        embed = discord.Embed(description=f"[{player.name}]({player.share_link}) removed from **server** legends tracking.",
                              color=discord.Color.green())
        return await ctx.send(embed=embed)




    async def check_global_tracked(self,player):
        results = await ongoing_stats.find_one({"tag": f"{player.tag}"})
        return results != None

    async def check_server_tracked(self,player, server_id):
        results = await server_db.find_one({"server": server_id})
        tracked_members = results.get("tracked_members")

        results = await ongoing_stats.find_one({"tag": player.tag})
        if results != None:
            servers = []
            servers = results.get("servers")
            if servers == None:
                servers = []
        else:
            servers = []

        return ((player.tag in tracked_members) or (server_id in servers))


    async def valid_player_check(self, ctx, player):
        if player is None:
            embed = discord.Embed(description="Not a valid player tag. Check the spelling or a different tag.",
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
            return False

        if str(player.league) != "Legend League":
            embed = discord.Embed(description="Sorry, cannot track players that are not in legends.",
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
            return False

        return True


def setup(bot: commands.Bot):
    bot.add_cog(track(bot))