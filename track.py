from discord.ext import commands
from clashClient import getPlayer, getClan
import discord

import certifi
ca = certifi.where()

import motor.motor_asyncio
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
ongoing_db = client.legends_stats
ongoing_stats = ongoing_db.ongoing_stats
settings = ongoing_db.settings

from tinydb import TinyDB, Query
botDb = TinyDB('botStuff.json')

class track(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(pass_context=True, invoke_without_command=True)
    async def feed(self, ctx, *, extra):
        results = await settings.find_one({"server_id": ctx.guild.id})
        if results == None:
            embed = discord.Embed(
                description="Sorry this server does not have a legends feed. Those with Manage Guild Perms can add one with **do setfeed #channel**.",
                color=discord.Color.red())
            return await ctx.send(embed=embed)

        fchannel = results.get("channel_id")

        if fchannel == None:
            embed = discord.Embed(
                description="Sorry this server does not have a legends feed. Those with Manage Guild Perms can add one with **do setfeed #channel**.",
                color=discord.Color.red())
            return await ctx.send(embed=embed)

        #pull player from tag, if none, return error
        player = await getPlayer(extra)
        if player is None:
            embed = discord.Embed(description="Not a valid player tag. Check the spelling or a different tag.",
                                  color=discord.Color.red())
            return await ctx.send(embed=embed)

        if str(player.league) != "Legend League":
            embed = discord.Embed(description="Sorry, cannot track players that are not in legends.",
                                  color=discord.Color.red())
            return await ctx.send(embed=embed)

        #lookup player for stats, if results, tracked
        results = await ongoing_stats.find_one({"tag" : f"{player.tag}"})
        if results is not None:
            feed_servers = results.get("servers")
            if ctx.guild.id in feed_servers:
                embed = discord.Embed(description=f"{player.name} is already being tracked & in your legends feed.",
                                      color=discord.Color.red())
                return await ctx.send(embed=embed)
            else:
                await ongoing_stats.update_one({'tag': f"{player.tag}"},
                                             {'$push': {'servers': ctx.guild.id}})
                embed = discord.Embed(description=f"{player.name} added to your legends feed.",
                                      color=discord.Color.green())
                return await ctx.send(embed=embed)
        else:
            clanName = "No Clan"
            if player.clan != None:
                clanName = player.clan.name

            embed = discord.Embed(description=f"{player.name} ({player.tag}) | {clanName} was added for legends tracking & to your legends feed.",
                                  color=discord.Color.green())
            await ctx.send(embed=embed)

            await ongoing_stats.insert_one({
                "tag": player.tag,
                "name": player.name,
                "trophies": player.trophies,
                "num_season_hits": player.attack_wins,
                "num_season_defenses": player.defense_wins,
                "row_triple": 0,
                "today_hits": [],
                "today_defenses": [],
                "num_today_hits": 0,
                "previous_hits": [],
                "previous_defenses": [],
                "num_yesterday_hits": 0,
                "end_of_day": [],
                "servers": [ctx.guild.id],
                "clan": clanName,
                "change": None,
                "link": player.share_link,
                "league" : str(player.league)
            })

    @commands.group(pass_context=True, invoke_without_command=True)
    async def track(self, ctx, *, extra):

        # pull player from tag, if none, return error
        player = await getPlayer(extra)
        if player is None:
            embed = discord.Embed(description="Not a valid player tag. Check the spelling or a different tag.",
                                  color=discord.Color.red())
            return await ctx.send(embed=embed)

        if str(player.league) != "Legend League":
            embed = discord.Embed(description="Sorry, cannot track players that are not in legends.",
                                  color=discord.Color.red())
            return await ctx.send(embed=embed)

        # lookup player for stats, if results, tracked
        results = await ongoing_stats.find_one({"tag": f"{player.tag}"})
        if results is not None:
            embed = discord.Embed(description=f"{player.name} is already being tracked.",
                                  color=discord.Color.red())
            return await ctx.send(embed=embed)

        else:
            clanName = "No Clan"
            if player.clan != None:
                clanName = player.clan.name

            embed = discord.Embed(
                description=f"{player.name} ({player.tag}) | {clanName} was added for legends tracking.",
                color=discord.Color.green())
            await ctx.send(embed=embed)

            await ongoing_stats.insert_one({
                "tag": player.tag,
                "name": player.name,
                "trophies": player.trophies,
                "num_season_hits": player.attack_wins,
                "num_season_defenses": player.defense_wins,
                "row_triple": 0,
                "today_hits": [],
                "today_defenses": [],
                "num_today_hits": 0,
                "previous_hits": [],
                "previous_defenses": [],
                "num_yesterday_hits": 0,
                "end_of_day": [],
                "servers": [],
                "clan": clanName,
                "change": None,
                "link": player.share_link,
                "league": str(player.league)
            })

    @commands.command(name='ctrack')
    @commands.is_owner()
    async def ctrack(self, ctx, *, extra):

        clan = await getClan(extra)

        if clan is None:
            embed = discord.Embed(description="Not a valid clan tag. Check the spelling or a different tag.",
                                  color=discord.Color.red())
            return await ctx.send(embed=embed)

        x = 0
        async for player in clan.get_detailed_members():
            if str(player.league) == "Legend League":
                results = await ongoing_stats.find_one({"tag" : f"{player.tag}"})
                if results is None:
                    x += 1
                    await ongoing_stats.insert_one({
                        "tag": player.tag,
                        "name": player.name,
                        "trophies": player.trophies,
                        "num_season_hits": player.attack_wins,
                        "num_season_defenses": player.defense_wins,
                        "row_triple": 0,
                        "today_hits": [],
                        "today_defenses": [],
                        "num_today_hits" : 0,
                        "previous_hits": [],
                        "previous_defenses": [],
                        "num_yesterday_hits": 0,
                        "end_of_day": [],
                        "servers": [],
                        "clan": clan.name,
                        "change": None,
                        "link" : player.share_link,
                        "league": str(player.league)
                    })

        embed = discord.Embed(description=f"{x} new people tracked from {clan.name}.",
                              color=discord.Color.green())
        return await ctx.send(embed=embed)

    @commands.group(pass_context=True, invoke_without_command=True)
    async def cfeed(self, ctx, *, extra):
        results = await settings.find_one({"server_id": ctx.guild.id})
        if results == None:
            embed = discord.Embed(
                description="Sorry this server does not have a legends feed. Those with Manage Guild Perms can add one with **do setfeed #channel**.",
                color=discord.Color.red())
            return await ctx.send(embed=embed)

        fchannel = results.get("channel_id")

        if fchannel == None:
            embed = discord.Embed(
                description="Sorry this server does not have a legends feed. Those with Manage Guild Perms can add one with **do setfeed #channel**.",
                color=discord.Color.red())
            return await ctx.send(embed=embed)

        clan = await getClan(extra)

        if clan is None:
            embed = discord.Embed(description="Not a valid clan tag. Check the spelling or a different tag.",
                                  color=discord.Color.red())
            return await ctx.send(embed=embed)

        x = 0
        async for player in clan.get_detailed_members():
            if str(player.league) == "Legend League":
                results = await ongoing_stats.find_one({"tag": f"{player.tag}"})
                if results is None:
                    x += 1
                    await ongoing_stats.insert_one({
                        "tag": player.tag,
                        "name": player.name,
                        "trophies": player.trophies,
                        "num_season_hits": player.attack_wins,
                        "num_season_defenses": player.defense_wins,
                        "row_triple": 0,
                        "today_hits": [],
                        "today_defenses": [],
                        "num_today_hits": 0,
                        "previous_hits": [],
                        "previous_defenses": [],
                        "num_yesterday_hits": 0,
                        "end_of_day": [],
                        "servers": [ctx.guild.id],
                        "clan": clan.name,
                        "change": None,
                        "link": player.share_link,
                        "league": str(player.league)
                    })
                else:
                    feed_servers = results.get("servers")
                    if ctx.guild.id not in feed_servers:
                        x += 1
                        await ongoing_stats.update_one({'tag': f"{player.tag}"},
                                                       {'$push': {'servers': ctx.guild.id}})

        embed = discord.Embed(description=f"{x} new people added to feed from {clan.name}.",
                              color=discord.Color.green())
        return await ctx.send(embed=embed)

    @cfeed.group(name="remove", pass_context=True, invoke_without_command=True)
    async def cfeedRemove(self, ctx,*, extra):
        results = await settings.find_one({"server_id": ctx.guild.id})
        if results == None:
            embed = discord.Embed(
                description="Sorry this server does not have a legends feed. Those with Manage Guild Perms can add one with **do setfeed #channel**.",
                color=discord.Color.red())
            return await ctx.send(embed=embed)

        fchannel = results.get("channel_id")

        if fchannel == None:
            embed = discord.Embed(
                description="Sorry this server does not have a legends feed. Those with Manage Guild Perms can add one with **do setfeed #channel**.",
                color=discord.Color.red())
            return await ctx.send(embed=embed)

        clan = await getClan(extra)

        if clan is None:
            embed = discord.Embed(description="Not a valid clan tag. Check the spelling or a different tag.",
                                  color=discord.Color.red())
            return await ctx.send(embed=embed)

        x = 0
        async for player in clan.get_detailed_members():
            if str(player.league) == "Legend League":
                results = await ongoing_stats.find_one({"tag": f"{player.tag}"})
                if results is not None:
                    feed_servers = results.get("servers")
                    if ctx.guild.id in feed_servers:
                        x += 1
                        await ongoing_stats.update_one({'tag': f"{player.tag}"},
                                                       {'$pull': {'servers': ctx.guild.id}})

        embed = discord.Embed(description=f"{x} people removed from feed from {clan.name}.",
                              color=discord.Color.green())
        return await ctx.send(embed=embed)


    @track.group(name= "remove", pass_context=True, invoke_without_command=True)
    @commands.is_owner()
    async def trackRemove(self, ctx, *, extra):
        player = await getPlayer(extra)
        if player is None:
            embed = discord.Embed(description="Not a valid player tag. Check the spelling or use a different tag.",
                                  color=discord.Color.red())
            return await ctx.send(embed=embed)

        results = await ongoing_stats.find_one({"tag" : f"{player.tag}"})
        if results is None:
            embed = discord.Embed(description="This player is not tracked at this time.",
                                  color=discord.Color.red())
            return await ctx.send(embed=embed)

        embed = discord.Embed(description=f"{player.name} removed from legends tracking.",
                              color=discord.Color.green())
        await ongoing_stats.find_one_and_delete({"tag" : f"{player.tag}"})
        return await ctx.send(embed=embed)

    @feed.group(name="remove", pass_context=True, invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def feedRemove(self,ctx, *, extra):
        results = await settings.find_one({"server_id": ctx.guild.id})
        if results == None:
            embed = discord.Embed(
                description="Sorry this server does not have a legends feed. Those with Manage Guild Perms can add one with **do setfeed #channel**.",
                color=discord.Color.red())
            return await ctx.send(embed=embed)

        fchannel = results.get("channel_id")

        if fchannel == None:
            embed = discord.Embed(
                description="Sorry this server does not have a legends feed. Those with Manage Guild Perms can add one with **do setfeed #channel**.",
                color=discord.Color.red())
            return await ctx.send(embed=embed)

        player = await getPlayer(extra)
        if player is None:
            embed = discord.Embed(description="Not a valid player tag. Check the spelling or a different tag.",
                                  color=discord.Color.red())
            return await ctx.send(embed=embed)

        # lookup player for stats, if results, tracked
        results = await ongoing_stats.find_one({"tag": f"{player.tag}"})
        if results is not None:
            feed_servers = results.get("servers")
            if ctx.guild.id not in feed_servers:
                embed = discord.Embed(description=f"{player.name} is not in your legends feed.",
                                      color=discord.Color.red())
                return await ctx.send(embed=embed)
            else:
                await ongoing_stats.update_one({'tag': f"{player.tag}"},
                                               {'$pull': {'servers': ctx.guild.id}})
                embed = discord.Embed(description=f"{player.name} removed from your legends feed.",
                                      color=discord.Color.green())
                return await ctx.send(embed=embed)

    @track.error
    @feed.error
    @cfeedRemove.error
    @feedRemove.error
    async def track_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                description="**PlayerTag argument missing.**\n`do track #playertag`\n`do feed #playertag`",
                color=discord.Color.red())
            await ctx.send(embed=embed)




def setup(bot: commands.Bot):
    bot.add_cog(track(bot))