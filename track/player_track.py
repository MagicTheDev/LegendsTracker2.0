from disnake.ext import commands
from utils.helper import getPlayer, ongoing_stats, server_db
from utils.db import addLegendsPlayer_SERVER, addLegendsPlayer_GLOBAL, removeLegendsPlayer_SERVER
import disnake


### SERVER MODEL###
"""
server_db.insert_one({
    "server": guild.id,
    "tracked_members": [],
})
"""

class PlayerTrack(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.slash_command(name="track", description="stuff")
    async def track(self, ctx):
        pass


    @track.sub_command(name="add", description="Add legends tracking for a player")
    async def track_add(self,ctx, player_tag):
        """
            Parameters
            ----------
            player_tag: player to add
        """
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
            embed = disnake.Embed(
                description="Sorry this command cannot be used while you have more than 500 people tracked and have feed enabled.\n"
                            "Please clear some members with `/clear_under`, sync members with `/clan_track sync`, or remove individual accounts with `/track remove`",
                color=disnake.Color.red())
            return await ctx.send(embed=embed)

        if is_global_tracked and is_server_tracked:
            embed = disnake.Embed(description=f"{player.name} is already globally & server tracked.",
                                  color=disnake.Color.green())
            return await ctx.send(embed=embed)
        elif is_global_tracked and not is_server_tracked:
            if is_full:
                embed = disnake.Embed(description=f"**This player is already globally tracked**\nHowever, cannot server track this player. Feed is full - has 500 players.\n"
                                                  f"Please clear some members with `/clear_under`, sync members with `/clan_track sync`, or remove individual accounts with `/track remove`",
                                      color=disnake.Color.from_rgb(255,255,0))
                return await ctx.send(embed=embed)
            else:
                embed = disnake.Embed(description=f"{player.name} added to server tracking.",
                                      color=disnake.Color.green())
                await addLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)

                return await ctx.send(embed=embed)
        else:
            if is_full:
                embed = disnake.Embed(description=f"**Player added for global tracking.**\n However, cannot server track this player. Feed is full - has 500 players.\n"
                                                  f"Please clear some members with `/clear_under`, sync members with `/clan_track sync`, or remove individual accounts with `/track remove`",
                                      color=disnake.Color.from_rgb(255,255,0))
                await ctx.send(embed=embed)

            clan_name = "No Clan"
            if player.clan is not None:
                clan_name = player.clan.name


            await addLegendsPlayer_GLOBAL(player=player, clan_name=clan_name)
            if not is_full:
                await addLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)

            embed = disnake.Embed(
                description=f"[{player.name}]({player.share_link}) | {clan_name} was added for legends tracking.",
                color=disnake.Color.green())
            await ctx.send(embed=embed)



    @track.sub_command(name="remove", description="Remove server legends tracking for a player")
    async def track_remove(self,ctx, player_tag : str):
        """
            Parameters
            ----------
            player_tag: player to remove
        """
        player = await getPlayer(player_tag)
        if player is None:
            embed = disnake.Embed(description=f"`{player_tag}` not a valid player tag. Check the spelling or use a different tag.",
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)

        is_server_tracked = await self.check_server_tracked(player=player, server_id=ctx.guild.id)
        if not is_server_tracked:
            embed = disnake.Embed(description="This player is not server tracked at this time.",
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)

        await removeLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)
        embed = disnake.Embed(description=f"[{player.name}]({player.share_link}) removed from **server** legends tracking.",
                              color=disnake.Color.green())
        return await ctx.send(embed=embed)






    async def check_global_tracked(self,player):
        results = await ongoing_stats.find_one({"tag": f"{player.tag}"})
        return results is not None

    async def check_server_tracked(self,player, server_id):
        results = await server_db.find_one({"server": server_id})
        tracked_members = results.get("tracked_members")

        results = await ongoing_stats.find_one({"tag": player.tag})
        if results is not None:
            servers = []
            servers = results.get("servers")
            if servers is None:
                servers = []
        else:
            servers = []

        return ((player.tag in tracked_members) or (server_id in servers))


    async def valid_player_check(self, ctx, player):
        if player is None:
            embed = disnake.Embed(description="Not a valid player tag. Check the spelling or a different tag.",
                                  color=disnake.Color.red())
            await ctx.send(embed=embed)
            return False

        if str(player.league) != "Legend League":
            embed = disnake.Embed(description="Sorry, cannot track players that are not in legends.",
                                  color=disnake.Color.red())
            await ctx.send(embed=embed)
            return False

        return True


