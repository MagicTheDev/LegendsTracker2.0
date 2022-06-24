from disnake.ext import commands
from utils.helper import getPlayer, ongoing_stats, server_db, has_guild_plan, has_single_plan, decrement_usage, translate, highest_tier
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
    async def track_add(self,ctx: disnake.ApplicationCommandInteraction, player_tag):
        """
            Parameters
            ----------
            player_tag: player to add
        """
        SINGLE_PLAN = await has_single_plan(ctx)
        GUILD_PLAN = await has_guild_plan(ctx)
        TIER, NUM_COMMANDS, MESSAGE = await decrement_usage(ctx, SINGLE_PLAN, GUILD_PLAN)
        if MESSAGE is not None:
            await ctx.response.defer(ephemeral=True)
            return await ctx.send(content=MESSAGE)

        TIER = await highest_tier(ctx)
        LIMITS = {0: 50, 1: 50, 2: 250, 3: 500}

        # pull player from tag, check if valid player or in legends
        player = await getPlayer(player_tag)
        valid = await self.valid_player_check(ctx=ctx, player=player)
        if not valid:
            return

        is_server_tracked = await self.check_server_tracked(player, ctx.guild.id)
        is_global_tracked = await self.check_global_tracked(player)

        results = await server_db.find_one({"server": ctx.guild.id})
        tracked_members = results.get("tracked_members")

        limit = LIMITS[TIER]
        is_full = (len(tracked_members) > limit)

        if len(tracked_members) > limit:
            embed = disnake.Embed(
                description=translate("choose_limit", ctx).format(num=limit),
                color=disnake.Color.red())
            return await ctx.send(embed=embed)

        if is_global_tracked and is_server_tracked:
            embed = disnake.Embed(description=translate("already_glob_serv_tracked",ctx).format(player_name=player.name),
                                  color=disnake.Color.green())
            return await ctx.send(embed=embed)
        elif is_global_tracked and not is_server_tracked:
            if is_full:
                embed = disnake.Embed(description=translate("choose_limit", ctx).format(num=limit),
                                      color=disnake.Color.from_rgb(255,255,0))
                return await ctx.send(embed=embed)
            else:
                embed = disnake.Embed(description=translate("already_glob_add_server",ctx).format(player_name=player.name),
                                      color=disnake.Color.green())
                page_buttons = [
                    disnake.ui.Button(label=translate("yes", ctx), emoji="✅", style=disnake.ButtonStyle.green,
                                      custom_id="Yes"),
                    disnake.ui.Button(label=translate("no", ctx), emoji="❌", style=disnake.ButtonStyle.red,
                                      custom_id="No")
                ]
                buttons = disnake.ui.ActionRow()
                for button in page_buttons:
                    buttons.append_item(button)

                await ctx.send(embed=embed, components=[buttons])
                msg = await ctx.original_message()

                def check(res: disnake.MessageInteraction):
                    return res.message.id == msg.id

                chose = False
                while chose is False:
                    try:
                        res: disnake.MessageInteraction = await self.bot.wait_for("message_interaction", check=check,
                                                                                  timeout=120)
                    except:
                        await msg.edit(components=[])
                        break

                    if res.author.id != ctx.author.id:
                        await res.send(content=translate("must_run_interact", ctx), ephemeral=True)
                        continue

                    chose = res.data.custom_id

                    if chose == "No":
                        embed = disnake.Embed(description=translate("player_track_canceled", ctx).format(player_tag=player_tag),
                                              color=disnake.Color.green())
                        return await res.response.edit_message(embed=embed,
                                                               components=[])

                embed = disnake.Embed(description=translate("added_server_tracking", ctx).format(player_name=player.name),
                                      color=disnake.Color.green())
                await addLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)
                return await ctx.edit_original_message(embed=embed, components=[])
        else:
            if is_full:
                embed = disnake.Embed(description=translate("added_glob_no_server", ctx).format(num=limit),
                                      color=disnake.Color.from_rgb(255,255,0))
                await ctx.send(embed=embed)

            clan_name = "No Clan"
            if player.clan is not None:
                clan_name = player.clan.name


            await addLegendsPlayer_GLOBAL(player=player, clan_name=clan_name)
            if not is_full:
                await addLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)

            embed = disnake.Embed(
                description=f"[{player.name}]({player.share_link}) | {clan_name} {translate('added_tracking', ctx)} ",
                color=disnake.Color.green())
            await ctx.send(embed=embed)



    @track.sub_command(name="remove", description="Remove server legends tracking for a player")
    async def track_remove(self,ctx, player_tag : str):
        """
            Parameters
            ----------
            player_tag: player to remove
        """
        SINGLE_PLAN = await has_single_plan(ctx)
        GUILD_PLAN = await has_guild_plan(ctx)
        TIER, NUM_COMMANDS, MESSAGE = await decrement_usage(ctx, SINGLE_PLAN, GUILD_PLAN)
        if MESSAGE is not None:
            await ctx.response.defer(ephemeral=True)
            return await ctx.send(content=MESSAGE)

        player = await getPlayer(player_tag)
        if player is None:
            embed = disnake.Embed(description=f"`{player_tag}` {translate('not_valid_player', ctx)}",
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)

        is_server_tracked = await self.check_server_tracked(player=player, server_id=ctx.guild.id)
        if not is_server_tracked:
            embed = disnake.Embed(description=translate("not_server_tracked", ctx),
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)

        await removeLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)
        embed = disnake.Embed(description=f"[{player.name}]({player.share_link}) {translate('removed_server_tracking2', ctx)}",
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
            embed = disnake.Embed(description=translate("not_valid_player", ctx),
                                  color=disnake.Color.red())
            await ctx.send(embed=embed)
            return False

        if str(player.league) != "Legend League":
            embed = disnake.Embed(description=translate("cannot_track_not_legends", ctx),
                                  color=disnake.Color.red())
            await ctx.send(embed=embed)
            return False

        return True


