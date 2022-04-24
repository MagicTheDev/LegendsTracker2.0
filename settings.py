from disnake.ext import commands
import disnake
from utils.helper import server_db, coc_client, getClan, clan_feed_db
from utils.db import removeLegendsPlayer_SERVER
from utils.components import create_components, create_components2
from coc import utils


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
            description=f"Feed channel setup.\nView feeds with `/feed list`",
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


    @commands.slash_command(name='tracked-list',description="List of clans or players tracked in server.")
    async def tracked_lists(self, ctx: disnake.ApplicationCommandInteraction, list_type: str = commands.Param(choices=["Clan list", "Player list"])):
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
        await ctx.edit_original_message(embed=embeds[0], components=create_components2(current_page, embeds, True))

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
                                                components=create_components2(current_page, embeds, True))

            elif res.data.custom_id == "Next":
                current_page += 1
                await res.response.edit_message(embed=embeds[current_page],
                                                components=create_components2(current_page, embeds, True))

            elif res.data.custom_id == "Print":
                await msg.delete()
                for embed in embeds:
                    await ctx.channel.send(embed=embed)


    @commands.slash_command(name='feed_defenses',
                            description="Turn feed defenses on & off")
    async def tracked_list(self, ctx: disnake.ApplicationCommandInteraction,
                           option: str = commands.Param(choices=["On", "Off"])):
        await server_db.update_one({"server": ctx.guild.id}, {'$set': {"feed_def": option}})
        embed = disnake.Embed(
            description=f"Feed defenses turned `{option}`",
            color=disnake.Color.green())
        return await ctx.send(embed=embed)

    @commands.slash_command(name="clan-feed")
    async def clan_feed(self, ctx: disnake.ApplicationCommandInteraction):
        pass

    @clan_feed.sub_command(name="add", description="Add a feed, in the channel ran, for a clan")
    async def clan_feed_add(self, ctx: disnake.ApplicationCommandInteraction, clan_tag: str):
        """
            Parameters
            ----------
            clan_tag: Clan to create feed for
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

        results = await clan_feed_db.find_one({"$and": [
            {"clan_tag": clan.tag},
            {"server": ctx.guild.id}
        ]})

        server_results = await server_db.find_one({"server": ctx.guild.id})
        main_feed = server_results.get("webhook")

        clan_webhooks = []
        clan_results = clan_feed_db.find({"server": ctx.guild.id})
        l = await clan_feed_db.count_documents(filter={"server": ctx.guild.id})
        if l == 5:
            embed = disnake.Embed(description="This server has the meximum of 5 clan feeds, remove one before adding another.",
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)
        for re in await clan_results.to_list(length=l):
            webh = re.get("webhook")
            clan_webhooks.append(webh)

        if results is None:
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
                    if w.id == main_feed or w.id in clan_webhooks:
                        embed = disnake.Embed(description="Another feed already set up here, use a different channel or thread.",
                                              color=disnake.Color.red())
                        return await ctx.send(embed=embed)

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

            if not is_thread:
                await clan_feed_db.insert_one({
                    "clan_tag" : clan.tag,
                    "server" : ctx.guild.id,
                    "webhook" : webhook.id,
                    "thread" : None
                })
            else:
                await clan_feed_db.insert_one({
                    "clan_tag": clan.tag,
                    "server": ctx.guild.id,
                    "webhook": webhook.id,
                    "thread": ctx.channel.id
                })

            if is_thread:
                await webhook.send("Test, Feed Successfully Setup", username='Legends Tracker',
                                   avatar_url="https://cdn.discordapp.com/attachments/843624785560993833/938961364100190269/796f92a51db491f498f6c76fea759651_1.png",
                                   thread=ctx.channel)

            else:
                await webhook.send("Test, Feed Successfully Setup", username='Legends Tracker',
                                   avatar_url="https://cdn.discordapp.com/attachments/843624785560993833/938961364100190269/796f92a51db491f498f6c76fea759651_1.png")

            embed = disnake.Embed(description=f"{clan.name} feed now set up.\nView all feeds & status with `/feed list`",
                                  color=disnake.Color.green())
            return await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(
                description=f"{clan.name} already has a feed set up.\nView all feeds & status with `/feed list`",
                color=disnake.Color.red())
            return await ctx.send(embed=embed)

    @clan_feed.sub_command(name="remove", description="Removes a feed for a clan")
    async def clan_feed_remove(self, ctx: disnake.ApplicationCommandInteraction, clan_tag: str):
        """
            Parameters
            ----------
            clan_tag: Clan to create feed for
        """
        perms = ctx.author.guild_permissions.manage_guild
        if not perms:
            embed = disnake.Embed(description="Command requires `Manage Server` permissions.",
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)

        clan_tag = utils.correct_tag(clan_tag)

        results = await clan_feed_db.find_one({"$and": [
            {"clan_tag": clan_tag},
            {"server": ctx.guild.id}
        ]})

        if results is None:
            embed = disnake.Embed(description="This clan does not have a feed set up.",
                                  color=disnake.Color.red())
            return await ctx.send(embed=embed)
        else:
            await clan_feed_db.find_one_and_delete({"$and": [
                {"clan_tag": clan_tag},
                {"server": ctx.guild.id}
            ]})
            clan = await getClan(clan_tag)
            if clan is None:
                embed = disnake.Embed(description="Clan feed removed.",
                                      color=disnake.Color.green())
                return await ctx.send(embed=embed)
            else:
                embed = disnake.Embed(description=f"{clan.name} feed removed.",
                                      color=disnake.Color.green())
                return await ctx.send(embed=embed)

    @feed.sub_command(name="list", description="List of feeds on this server")
    async def feed_list(self, ctx: disnake.ApplicationCommandInteraction):
        server_results = await server_db.find_one({"server": ctx.guild.id})
        main_feed = server_results.get("webhook")
        main_thread = server_results.get("thread")

        channel = ""

        if main_thread is None:
            try:
                webhook: disnake.Webhook = await self.bot.fetch_webhook(main_feed)
                channel = webhook.channel.mention
            except:
                channel = None
        else:
            try:
                channel = await self.bot.fetch_channel(main_thread)
                channel = channel.mention
            except:
                channel = None

        text = f"Main Feed: {channel}\n"

        clan_results = clan_feed_db.find({"server": ctx.guild.id})
        l = await clan_feed_db.count_documents(filter={"server": ctx.guild.id})
        for re in await clan_results.to_list(length=l):
            webhook = re.get("webhook")
            thread = re.get("thread")
            clan_tag = re.get("clan_tag")

            clan = await getClan(clan_tag)
            if clan is None:
                clan = ""
            else:
                clan = clan.name

            if thread is None:
                try:
                    webhook: disnake.Webhook = await self.bot.fetch_webhook(webhook)
                    channel = webhook.channel.mention
                except:
                    channel = None
            else:
                try:
                    channel = await self.bot.fetch_channel(thread)
                    channel = channel.mention
                except:
                    channel = None

            text += f"{clan} ({clan_tag}) | Feed: {channel}\n"

        embed = disnake.Embed(title="Server Feed List",
            description=text,
            color=disnake.Color.green())
        return await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(bot_settings(bot))
