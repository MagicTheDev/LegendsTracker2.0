from disnake.ext import commands
from utils.helper import getClan, ongoing_stats, server_db, coc_client
from utils.db import addLegendsPlayer_SERVER, addLegendsPlayer_GLOBAL, removeLegendsPlayer_SERVER
import disnake

### SERVER MODEL###
"""
server_db.insert_one({
    "server": guild.id,
    "tracked_members": [],
})
"""

class ClanTrack(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="ctrack", description="Clan tracking")
    async def ctrack(self, ctx):
        pass

    @ctrack.sub_command(name="add", description="Add players in a clan to legends tracking" )
    async def ctrack_add(self,ctx: disnake.ApplicationCommandInteraction, clan_tag: str):
        """
            Parameters
            ----------
            clan_tag: Clan to track
          """

        perms = ctx.author.guild_permissions.manage_guild
        if not perms:
            embed = disnake.Embed(description="Command requires `Manage Server` permissions.",
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)

        clan = await getClan(clan_tag)
        if clan is None:
            embed = disnake.Embed(description="Not a valid clan tag. Check the spelling or a different tag.",
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)

        results = await server_db.find_one({"server": ctx.guild.id})
        tracked_clans = results.get("tracked_clans")
        if tracked_clans is None:
            tracked_clans = []

        if clan.tag in tracked_clans:
            embed = disnake.Embed(description="Clan already tracked.\nUse `/clan_track sync` to sync your feed with players from this clan.",
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)

        tracked_members = results.get("tracked_members")
        feed = results.get("channel_id")
        if len(tracked_members) > 500 and feed is not None:
            embed = disnake.Embed(
                description="Sorry this command cannot be used while you have more than 500 people tracked and have feed enabled.\n"
                            "Please clear some members with `/clear_under`, sync members with `/clan_track sync`, or remove individual accounts with `/track remove`",
                color=disnake.Color.red())
            return await ctx.send(embed=embed)

        allowed_num = await self.sync_limit(ctx)
        if len(tracked_clans) >= allowed_num:
            embed = disnake.Embed(
                description="Sorry you have linked the max amount of clans.\n"
                            "All patreons can link up to 20 clans.",
                color=disnake.Color.red())
            return await ctx.send(embed=embed)

        embed = disnake.Embed(
            description="<a:loading:884400064313819146> Adding players...",
            color=disnake.Color.green())
        await ctx.send(embed=embed)
        msg = await ctx.original_message()

        num_global_tracked = 0
        num_server_tracked = 0
        async for player in clan.get_detailed_members():
            if str(player.league) == "Legend League":
                is_global_tracked = await self.check_global_tracked(player=player)
                is_server_tracked = await self.check_server_tracked(player=player, server_id=ctx.guild.id)
                if not is_global_tracked:
                    num_global_tracked += 1
                    await addLegendsPlayer_GLOBAL(player=player,clan_name=clan.name)
                if not is_server_tracked:
                    num_server_tracked+=1
                    await addLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)


        await server_db.update_one({'server': ctx.guild.id},
                                   {'$push': {"tracked_clans": clan.tag}})

        embed = disnake.Embed(
                title=f"{clan.name} linked to your server.",
                description=f"{num_global_tracked} members added to global tracking.\n"
                            f"{num_server_tracked} members added to server tracking.",
                color=disnake.Color.green())
        embed.set_thumbnail(url=clan.badge.large)
        return await msg.edit(embed=embed)


    @ctrack.sub_command(name="remove", description="Remove players in a clan from legends tracking")
    async def ctrack_remove(self,ctx: disnake.ApplicationCommandInteraction, clan_tag: str):
        """
            Parameters
            ----------
            clan_tag: Clan to remove tracking from
        """
        await ctx.response.defer()

        perms = ctx.author.guild_permissions.manage_guild
        if not perms:
            embed = disnake.Embed(description="Command requires `Manage Server` permissions.",
                                  color=disnake.Color.red())
            return await ctx.edit_original_message(embed=embed)

        clan = await getClan(clan_tag)

        if clan is None:
            embed = disnake.Embed(description="Not a valid clan tag. Check the spelling or a different tag.",
                                  color=disnake.Color.red())
            return await ctx.edit_original_message(embed=embed)

        results = await server_db.find_one({"server": ctx.guild.id})
        tracked_clans = results.get("tracked_clans")
        if tracked_clans is None:
            tracked_clans = []

        if clan.tag not in tracked_clans:
            embed = disnake.Embed(
                description="Clan not tracked.\nUse `/clan_track add` to add this clan to your server.",
                color=disnake.Color.red())
            return await ctx.edit_original_message(embed=embed)

        num_server_tracked = 0
        async for player in clan.get_detailed_members():
            if str(player.league) == "Legend League":
                is_server_tracked = await self.check_server_tracked(player=player, server_id=ctx.guild.id)
                if is_server_tracked:
                    num_server_tracked += 1
                    await removeLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)

        await server_db.update_one({'server': ctx.guild.id},
                                   {'$pull': {"tracked_clans": clan.tag}})


        embed = disnake.Embed(
            title=f"{clan.name}",
            description=f"{num_server_tracked} members removed from server tracking.",
            color=disnake.Color.green())
        embed.set_thumbnail(url=clan.badge.large)
        await ctx.edit_original_message(embed=embed)


    @ctrack.sub_command(name="list", description="List of clans linked to server")
    async def ctrack_list(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.response.defer()

        results = await server_db.find_one({"server": ctx.guild.id})
        tracked_clans = results.get("tracked_clans")
        if tracked_clans is None:
            tracked_clans = []

        if tracked_clans == []:
            embed = disnake.Embed(
                description="No clans linked to this server.\nUse `clan_track add` to get started.",
                color=disnake.Color.red())
            return await ctx.send(embed=embed)

        text = ""
        async for clan in coc_client.get_clans(tracked_clans):
            text += f"{clan.name} | {clan.tag}\n"

        embed = disnake.Embed(title=f"{ctx.guild.name} Linked Clans",
            description=text,
            color=disnake.Color.blue())
        return await ctx.edit_original_message(embed=embed)


    @ctrack.sub_command(name="sync", description="Sync players with the clans linked to server")
    async def ctrack_sync(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.response.defer()

        perms = ctx.author.guild_permissions.manage_guild
        if not perms:
            embed = disnake.Embed(description="Command requires `Manage Server` permissions.",
                                  color=disnake.Color.red())
            return await ctx.edit_original_message(embed=embed)

        results = await server_db.find_one({"server": ctx.guild.id})
        tracked_clans = results.get("tracked_clans")
        if tracked_clans is None:
            tracked_clans = []

        if tracked_clans == []:
            embed = disnake.Embed(
                description="No clans linked to this server.\nUse `clan_track add` to get started.",
                color=disnake.Color.red())
            return await ctx.edit_original_message(embed=embed)

        embed = disnake.Embed(description=f"**Would you like to remove tracked players outside of the linked clans?**\n"
                                          f"if **yes**, this will set your feed & leaderboard to just members of the clans in `/clan_track` list.\n",
                              color=disnake.Color.green())

        select1 = disnake.ui.Select(
            options=[
                disnake.SelectOption(label="Yes", value=f"Yes", emoji="✅"),
                disnake.SelectOption(label="No", value=f"No", emoji="❌")
            ],
            placeholder="Choose your option",
            min_values=1,  # the minimum number of options a user must select
            max_values=1  # the maximum number of options a user can select
        )
        action_row = disnake.ui.ActionRow()
        action_row.append_item(select1)

        await ctx.edit_original_message(embed=embed, components=[action_row])
        msg = await ctx.original_message()

        chose = False

        def check(res: disnake.MessageInteraction):
            return res.message.id == msg.id

        while chose is False:
            try:
                res: disnake.MessageInteraction = await self.bot.wait_for("message_interaction", check=check,
                                                                          timeout=600)
            except:
                await msg.edit(components=[])
                break

            if res.author.id != ctx.author.id:
                await res.send(content="You must run the command to interact with components.", ephemeral=True)
                continue

            chose = res.values[0]
            # print(chose)

        if chose == "No":
            tracked_members = results.get("tracked_members")
            feed = results.get("channel_id")
            if len(tracked_members) > 500 and feed is not None:
                embed = disnake.Embed(
                    description="Sorry this command cannot be used while you have more than 500 people tracked and have feed enabled.\n"
                                "Please clear some members with `/clear_under`, sync members with `/clan_track sync`, or remove individual accounts with `/track remove`",
                    color=disnake.Color.red())
                return await msg.edit(embed=embed, components=[])

            num_global_tracked = 0
            num_server_tracked = 0
            async for clan in coc_client.get_clans(tracked_clans):
                async for player in clan.get_detailed_members():
                    if str(player.league) == "Legend League":
                        is_global_tracked = await self.check_global_tracked(player=player)
                        is_server_tracked = await self.check_server_tracked(player=player, server_id=ctx.guild.id)
                        if not is_global_tracked:
                            num_global_tracked += 1
                            await addLegendsPlayer_GLOBAL(player=player, clan_name=clan.name)
                        if not is_server_tracked:
                            num_server_tracked += 1
                            await addLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)

            embed = disnake.Embed(
                description=f"{num_global_tracked} members added to global tracking.\n"
                            f"{num_server_tracked} members added to server tracking.",
                color=disnake.Color.green())
            if ctx.guild.icon is not None:
                embed.set_thumbnail(url=ctx.guild.icon.url)
            return await msg.edit(embed=embed, components=[])
        else:
            num_global_tracked = 0
            num_server_tracked = 0
            players_to_be = []
            async for clan in coc_client.get_clans(tracked_clans):
                async for player in clan.get_detailed_members():
                    players_to_be.append(player.tag)
                    if str(player.league) == "Legend League":
                        is_global_tracked = await self.check_global_tracked(player=player)
                        is_server_tracked = await self.check_server_tracked(player=player, server_id=ctx.guild.id)
                        if not is_global_tracked:
                            num_global_tracked += 1
                            await addLegendsPlayer_GLOBAL(player=player, clan_name=clan.name)
                        if not is_server_tracked:
                            num_server_tracked += 1
                            await addLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)

            remove_num = 0
            tracked_members = results.get("tracked_members")
            for mem in tracked_members:
                if mem not in players_to_be:
                    remove_num += 1
                    await ongoing_stats.update_one({'tag': mem},
                                                   {'$pull': {"servers": ctx.guild.id}})
                    await server_db.update_one({'server': ctx.guild.id},
                                               {'$pull': {"tracked_members": mem}})

            embed = disnake.Embed(
                description=f"{num_global_tracked} members added to global tracking.\n"
                            f"{num_server_tracked} members added to server tracking.\n"
                            f"{remove_num} members removed from server tracking.",
                color=disnake.Color.green())
            if ctx.guild.icon is not None:
                embed.set_thumbnail(url=ctx.guild.icon.url)
            return await msg.edit(embed=embed, components=[])


    async def sync_limit(self, ctx):
        results = await server_db.find_one({"server": ctx.guild.id})
        pat = results.get("patreon_sub")
        if pat is not None:
            return 20
        return 10

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


