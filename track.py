from discord.ext import commands
from helper import getPlayer, getClan, ongoing_stats, server_db, addLegendsPlayer_SERVER, addLegendsPlayer_GLOBAL, removeLegendsPlayer_SERVER
import discord
from discord.commands import SlashCommandGroup, Option

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

        track = SlashCommandGroup(name="track",
                                  description="Commands to add legends tracking for players.",
                                  guild_ids=[328997757048324101, 923764211845312533])

        @track.command(name="add",description="Add legends tracking for a player.")
        async def track_add(ctx, player_tag : Option(str, description="Tag to track", required=True)):

            # pull player from tag, check if valid player or in legends
            player = await getPlayer(player_tag)
            await valid_player_check(ctx=ctx, player=player)

            is_server_tracked = await check_server_tracked(player, ctx.guild.id)
            is_global_tracked = await check_global_tracked(player)

            if is_global_tracked and is_server_tracked:
                embed = discord.Embed(description=f"{player.name} is already globally & server tracked.",
                                      color=discord.Color.green())
                return await ctx.respond(embed=embed)
            elif is_global_tracked and not is_server_tracked:
                embed = discord.Embed(description=f"{player.name} added to server tracking.",
                                      color=discord.Color.green())
                await addLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)

                return await ctx.respond(embed=embed)
            else:
                clan_name = "No Clan"
                if player.clan != None:
                    clan_name = player.clan.name

                await addLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)
                await addLegendsPlayer_GLOBAL(player=player, clan_name=clan_name)

                embed = discord.Embed(
                    description=f"[{player.name}] ({player.share_link}) | {clan_name} was added for legends tracking.",
                    color=discord.Color.green())
                await ctx.respond(embed=embed)


        @track.command(name="remove", description="Remove server legends tracking for a player.")
        async def track_remove(ctx, player_tag: Option(str, description="Tag to track", required=True)):
            player = await getPlayer(player_tag)
            if player is None:
                embed = discord.Embed(description=f"`{player_tag}` not a valid player tag. Check the spelling or use a different tag.",
                                      color=discord.Color.red())
                return await ctx.respond(embed=embed)

            is_server_tracked = await check_server_tracked(player=player, server_id=ctx.guild.id)
            if not is_server_tracked:
                embed = discord.Embed(description="This player is not server tracked at this time.",
                                      color=discord.Color.red())
                return await ctx.respond(embed=embed)

            await removeLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)
            embed = discord.Embed(description=f"[{player.name}] ({player.share_link}) removed from server legends tracking.",
                                  color=discord.Color.green())
            return await ctx.respond(embed=embed)

        ctrack = SlashCommandGroup(name="ctrack",
                                   description="Commands to add tracking of a clan of legends players.",
                                   guild_ids=[328997757048324101, 923764211845312533])

        @ctrack.command(name="add", description="Add players in a clan to legends tracking.")
        async def ctrack_add(ctx, clan_tag: Option(str, description="Tag to track", required=True)):
            await ctx.defer()

            perms = ctx.author.guild_permissions.manage_guild
            if not perms:
                embed = discord.Embed(description="Command requires `Manage Guild` permissions.",
                                      color=discord.Color.red())
                return await ctx.respond(embed=embed)

            clan = await getClan(clan_tag)
            if clan is None:
                embed = discord.Embed(description="Not a valid clan tag. Check the spelling or a different tag.",
                                      color=discord.Color.red())
                return await ctx.respond(embed=embed)

            num_global_tracked = 0
            num_server_tracked = 0
            async for player in clan.get_detailed_members():
                if str(player.league) == "Legend League":
                    is_global_tracked = await check_global_tracked(player=player)
                    is_server_tracked = await check_server_tracked(player=player, server_id=ctx.guild.id)
                    if not is_global_tracked:
                        num_global_tracked += 1
                        await addLegendsPlayer_GLOBAL(player=player,clan_name=clan.name)
                    if not is_server_tracked:
                        num_server_tracked+=1
                        await addLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)

            embed = discord.Embed(
                    title=f"{clan.name}",
                    description=f"{num_global_tracked} members added to global tracking.\n"
                                f"{num_server_tracked} members added to server tracking.",
                    color=discord.Color.green())
            embed.set_thumbnail(url=clan.badge.large)
            return await ctx.respond(embed=embed)

        @ctrack.command(name="remove", description="Remove players in a clan from legends tracking.")
        async def ctrack_remove(ctx, clan_tag: Option(str, description="Tag to track", required=True)):
            await ctx.defer()

            perms = ctx.author.guild_permissions.manage_guild
            if not perms:
                embed = discord.Embed(description="Command requires `Manage Guild` permissions.",
                                      color=discord.Color.red())
                return await ctx.respond(embed=embed)

            clan = await getClan(clan_tag)

            if clan is None:
                embed = discord.Embed(description="Not a valid clan tag. Check the spelling or a different tag.",
                                      color=discord.Color.red())
                return await ctx.respond(embed=embed)

            num_server_tracked = 0
            async for player in clan.get_detailed_members():
                if str(player.league) == "Legend League":
                    is_server_tracked = await check_server_tracked(player=player, server_id=ctx.guild.id)
                    if is_server_tracked:
                        num_server_tracked += 1
                        await removeLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)

            embed = discord.Embed(
                title=f"{clan.name}",
                description=f"{num_server_tracked} members removed from server tracking.",
                color=discord.Color.green())
            embed.set_thumbnail(url=clan.badge.large)
            return await ctx.respond(embed=embed)

        async def check_global_tracked(player):
            results = await ongoing_stats.find_one({"tag": f"{player.tag}"})
            return results != None

        async def check_server_tracked(player, server_id):
            results = await server_db.find_one({"server": server_id})
            tracked_members = results.get("tracked_members")
            return (player.tag in tracked_members)


        async def valid_player_check(ctx, player):
            if player is None:
                embed = discord.Embed(description="Not a valid player tag. Check the spelling or a different tag.",
                                      color=discord.Color.red())
                return await ctx.respond(embed=embed)

            if str(player.league) != "Legend League":
                embed = discord.Embed(description="Sorry, cannot track players that are not in legends.",
                                      color=discord.Color.red())
                return await ctx.respond(embed=embed)


        bot.add_application_command(track)
        bot.add_application_command(ctrack)



def setup(bot: commands.Bot):
    bot.add_cog(track(bot))