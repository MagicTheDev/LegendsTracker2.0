from discord.ext import commands
import discord
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, wait_for_component, create_select, create_select_option, create_actionrow
from discord_slash.model import ButtonStyle

from helper import server_db, coc_client, removeLegendsPlayer_SERVER


class bot_settings(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_subcommand(base='feed', name="set",
                       description="Set channel for attack/defense feed.",
                       options=[create_option(name="channel", option_type=7, description="Choose channel for feed.", required=True)])
    async def setfeed(self, ctx, channel=None):
        extra = channel.id
        perms = ctx.author.guild_permissions.manage_guild
        if ctx.author.id == 706149153431879760:
            perms = True
        if not perms:
            embed = discord.Embed(description="Command requires you to have `Manage Guild` permissions.",
                                  color=discord.Color.red())
            return await ctx.send(embed=embed)

        results = await server_db.find_one({"server": ctx.guild.id})

        if results == None:
            return

        typeC = str(channel.type)
        if typeC != "text":
            embed = discord.Embed(description=f"Must be a text channel, not {typeC} channel.",
                                  color=discord.Color.red())
            return await ctx.send(embed=embed)

        try:
            extra = await self.bot.fetch_channel(extra)
            c = extra
            g = ctx.guild
            r = await g.fetch_member(825324351016534036)
            perms = c.permissions_for(r)
            send_msg = perms.send_messages
            external_emoji = perms.use_external_emojis
            if send_msg == False or external_emoji == False:
                embed = discord.Embed(
                    description=f"Feed channel creation canceled. Missing Permissions in that channel.\nMust have `Send Messages` and `Use External Emojis` perms in the feed channel.\n `do setfeed none` to remove feed.",
                    color=discord.Color.red())
                return await ctx.send(embed=embed)
        except:
            embed = discord.Embed(
                description=f"Invalid Channel or Missing Access to view channel.\n`/feed remove` to remove feed.",
                color=discord.Color.red())
            return await ctx.send(embed=embed)

        channel = extra.id

        await server_db.update_one({"server": ctx.guild.id}, {'$set': {"channel_id": channel}})

        embed = discord.Embed(
            description=f"{extra.mention} set as feed channel.\nEnsure I have permission to send messages there.\nView current feed channel with `/stats`.",
            color=discord.Color.green())
        return await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="clear_under",
                       description="Top player stats - (hits, def, net).",
                       options=[
                           create_option(
                               name="previous",
                               description="Previous Top Stats",
                               option_type=3,
                               required=False,
                               choices=["5000", "5100", "5200", "5300", "5400", "5500", "5600", "5700", "5800", "5900", "6000"]
                           )
                       ]
                       )
    async def trophyLimit(self, ctx,  trophies):
        await ctx.defer()
        perms = ctx.author.guild_permissions.manage_guild
        if ctx.author.id == 706149153431879760:
            perms = True
        if not perms:
            embed = discord.Embed(description="Command requires you to have `Manage Server` permissions.",
                                  color=discord.Color.red())
            return await ctx.send(embed=embed)

        results = await server_db.find_one({"server": ctx.guild.id})

        if results == None:
            return

        fchannel = results.get("channel_id")
        if fchannel == None:
            embed = discord.Embed(
                description="Sorry this server does not have a legends feed. Those with Manage Server Perms can add one with **/feed set**.",
                color=discord.Color.red())
            return await ctx.send(embed=embed)
        trophies = int(trophies)

        tracked_members = results.get("tracked_members")

        num_clear = 0
        async for player in coc_client.get_players(tracked_members):
            if player.trophies < trophies:
                num_clear +=1
                await removeLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)

        embed = discord.Embed(
            description=f"<a:check:861157797134729256> Trophies below {trophies} cleared.\n"
                        f"{num_clear} accounts cleared.",
            color=discord.Color.green())
        return await ctx.send(embed=embed)


    @cog_ext.cog_subcommand(base='feed', name="remove",
                            description="Remove channel for attack/defense feed.")
    async def feed_remove(self, ctx):
        perms = ctx.author.guild_permissions.manage_guild
        if ctx.author.id == 706149153431879760:
            perms = True
        if not perms:
            embed = discord.Embed(description="Command requires you to have `Manage Server` permissions.",
                                  color=discord.Color.red())
            return await ctx.send(embed=embed)

        results = await server_db.find_one({"server": ctx.guild.id})

        await server_db.update_one({"server": ctx.guild.id}, {'$set': {"channel_id": None}})
        embed = discord.Embed(description=f"Feed channel removed.",
                              color=discord.Color.green())
        return await ctx.send(embed=embed)





    @cog_ext.cog_slash(name='tracked_list',
                       description="List of clans or players tracked in server.",
                       options=[
                           create_option(
                               name="list_type",
                               description="Choose clan or player tracked list",
                               option_type=3,
                               required=True,
                               choices=["Clan list", "Player list"]
                           )
                       ])
    async def tracked_list(self, ctx, list_type):
        await ctx.defer()
        list = []
        results = await server_db.find_one({"server": ctx.guild.id})
        tags = results.get("tracked_members")
        if tags == []:
            embed = discord.Embed(description="No players tracked on this server.",
                                  color=discord.Color.red())
            return await ctx.send(embed=embed)
        async for player in coc_client.get_players(tags):
            if list_type == "Clan list":
                if player.clan != None:
                    if player.clan not in list:
                        list.append(player.clan)
            else:
                list.append(player)

        text = ""
        x = 0
        embeds= []
        for l in list:
            text += f"{l.name} | {l.tag}\n"
            x += 1
            if x == 25:
                embed = discord.Embed(title=f"Tracked List ({len(list)} results)",description=f"{text}",
                                      color=discord.Color.blue())
                x = 0
                embeds.append(embed)
                text = ""

        if text != "":
            embed = discord.Embed(title=f"Tracked List ({len(list)} results)", description=f"{text}",
                                  color=discord.Color.blue())
            embeds.append(embed)

        current_page = 0
        msg = await ctx.send(embed=embeds[0], components=self.create_components(current_page, embeds))

        while True:
            try:
                res = await wait_for_component(self.bot, components=self.create_components(current_page, embeds),
                                               messages=msg, timeout=600)
            except:
                await msg.edit(components=[])
                break

            if res.author_id != ctx.author.id:
                await res.send(content="You must run the command to interact with components.", hidden=True)
                continue

            await res.edit_origin()

            # print(res.custom_id)
            if res.custom_id == "Previous":
                current_page -= 1
                await msg.edit(embed=embeds[current_page],
                               components=self.create_components(current_page, embeds))

            elif res.custom_id == "Next":
                current_page += 1
                await msg.edit(embed=embeds[current_page],
                               components=self.create_components(current_page, embeds))


    def create_components(self, current_page, embeds):
        length = len(embeds)
        if length == 1:
            return []

        page_buttons = [create_button(label="", emoji="◀️", style=ButtonStyle.blue, disabled=(current_page == 0),
                                      custom_id="Previous"),
                        create_button(label=f"Page {current_page + 1}/{length}", style=ButtonStyle.grey,
                                      disabled=True),
                        create_button(label="", emoji="▶️", style=ButtonStyle.blue,
                                      disabled=(current_page == length - 1), custom_id="Next")
                        ]
        page_buttons = create_actionrow(*page_buttons)

        return [page_buttons]









def setup(bot: commands.Bot):
    bot.add_cog(bot_settings(bot))