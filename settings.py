from disnake.ext import commands
import disnake
from utils.helper import server_db, coc_client
from utils.db import removeLegendsPlayer_SERVER
from utils.components import create_components


class bot_settings(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="feed", description="Check a player's legends stats")
    async def feed(self, ctx):
        pass


    @feed.sub_command(name= "set", description="Sets feed in the channel you run this command.")
    async def setfeed(self, ctx):

        perms = ctx.author.guild_permissions.manage_guild
        if ctx.author.id == 706149153431879760:
            perms = True
        if not perms:
            embed = disnake.Embed(description="Command requires **you** to have `Manage Guild` permissions.",
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)
        is_thread = False
        try:
            if "thread" in str(ctx.channel.type):
                is_thread = True
                channel = ctx.channel.parent
            else:
                channel = ctx.channel


            bot_av = self.bot.user.avatar.read().close()
            webhooks = await channel.webhooks()
            webhook = None
            for w in webhooks:
                if w.user.id == self.bot.user.id:
                    webhook = w
                    break
            if webhook is None:
                webhook = await channel.create_webhook(name="Legends Tracker", avatar=bot_av, reason="Legends Feed")


        except Exception as e:
            e = str(e)[0:1000]
            embed = disnake.Embed(title="Error",
                description="Likely Missing Permissions\nEnsure the bot has both `Manage Webhooks` and `Send Messages` Perms for this channel.\nError Output: " + e,
                color=disnake.Color.red())
            return await ctx.send(embed=embed)

        await server_db.update_one({"server": ctx.guild.id}, {'$set': {"webhook": webhook.id}})
        await server_db.update_one({"server": ctx.guild.id}, {'$set': {"thread": None}})
        if is_thread:
            await server_db.update_one({"server": ctx.guild.id}, {'$set': {"thread": ctx.channel.id}})
            await webhook.send("Feed Successfully Setup", username='Legends Tracker',
                               avatar_url="https://cdn.discordapp.com/attachments/843624785560993833/938961364100190269/796f92a51db491f498f6c76fea759651_1.png", thread=ctx.channel)

        else:
            await webhook.send("Feed Successfully Setup", username='Legends Tracker',
                                   avatar_url="https://cdn.discordapp.com/attachments/843624785560993833/938961364100190269/796f92a51db491f498f6c76fea759651_1.png")


        embed = disnake.Embed(
            description=f"Feed channel setup.\nView status of feed with `/stats`",
            color=disnake.Color.green())
        return await ctx.send(embed=embed)



    @commands.slash_command(name="clear_under",
                       description="Remove players under certain trophies from server tracking.")
    async def trophyLimit(self, ctx: disnake.ApplicationCommandInteraction, trophies: int):
        """
            Parameters
            ----------
            trophies: trophy bar to clear under
          """
        await ctx.response.defer()
        perms = ctx.author.guild_permissions.manage_guild
        if ctx.author.id == 706149153431879760:
            perms = True
        if not perms:
            embed = disnake.Embed(description="Command requires you to have `Manage Server` permissions.",
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)

        results = await server_db.find_one({"server": ctx.guild.id})

        if results is None:
            return

        trophies = int(trophies)

        tracked_members = results.get("tracked_members")

        num_clear = 0
        async for player in coc_client.get_players(tracked_members):
            if player.trophies < trophies:
                num_clear +=1
                await removeLegendsPlayer_SERVER(player=player, guild_id=ctx.guild.id)

        embed = disnake.Embed(
            description=f"<a:check:861157797134729256> Trophies below {trophies} cleared.\n"
                        f"{num_clear} accounts cleared.",
            color=disnake.Color.green())
        return await ctx.edit_original_message(embed=embed)


    @feed.sub_command(name="remove",
                            description="Remove channel for attack/defense feed.")
    async def feed_remove(self, ctx):
        perms = ctx.author.guild_permissions.manage_guild
        if ctx.author.id == 706149153431879760:
            perms = True
        if not perms:
            embed = disnake.Embed(description="Command requires you to have `Manage Server` permissions.",
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)

        await server_db.update_one({"server": ctx.guild.id}, {'$set': {"webhook": None}})
        await server_db.update_one({"server": ctx.guild.id}, {'$set': {"thread": None}})
        embed = disnake.Embed(description=f"Feed removed.",
                              color=disnake.Color.green())
        return await ctx.send(embed=embed)



    @commands.slash_command(name='tracked_list',
                       description="List of clans or players tracked in server.")
    async def tracked_list(self, ctx: disnake.ApplicationCommandInteraction, list_type: str = commands.Param(choices=["Clan list", "Player list"])):
        await ctx.response.defer()
        list = []
        results = await server_db.find_one({"server": ctx.guild.id})
        tags = results.get("tracked_members")
        if tags == []:
            embed = disnake.Embed(description="No players tracked on this server.",
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)
        async for player in coc_client.get_players(tags):
            if list_type == "Clan list":
                if player.clan is not None:
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
                embed = disnake.Embed(title=f"Tracked List ({len(list)} results)",description=f"{text}",
                                      color=disnake.Color.blue())
                x = 0
                embeds.append(embed)
                text = ""

        if text != "":
            embed = disnake.Embed(title=f"Tracked List ({len(list)} results)", description=f"{text}",
                                  color=disnake.Color.blue())
            embeds.append(embed)

        current_page = 0
        await ctx.edit_original_message(embed=embeds[0], components=create_components(current_page, embeds))

        msg = await ctx.original_message()

        def check(res: disnake.MessageInteraction):
            return res.message.id == msg.id

        while True:
            try:
                res = await self.bot.wait_for("message_interaction", check=check, timeout=600)
            except:
                await ctx.edit_original_message(components=[])
                break

            if res.author.id != ctx.author.id:
                await res.send(content="You must run the command to interact with components.", ephemeral=True)
                continue

            if res.data.custom_id == "Previous":
                current_page -= 1
                await res.response.edit_message(embed=embeds[current_page],
                                                components=create_components(current_page, embeds))

            elif res.data.custom_id == "Next":
                current_page += 1
                await res.response.edit_message(embed=embeds[current_page],
                                                components=create_components(current_page, embeds))






def setup(bot: commands.Bot):
    bot.add_cog(bot_settings(bot))
