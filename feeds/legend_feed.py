
import disnake
from disnake.ext import commands, tasks
import pytz
utc = pytz.utc
from utils.helper import server_db, ongoing_stats, clan_feed_db, getClan, coc_client
from utils.db import addLegendsPlayer_GLOBAL

class LegendsFeed(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.feed_update.start()

    def cog_unload(self):
        self.feed_update.cancel()

    @tasks.loop(seconds=300)
    async def feed_update(self):
        all_tags = []
        tracked = ongoing_stats.find()
        limit = await ongoing_stats.count_documents(filter={})
        for document in await tracked.to_list(length=limit):
            tag = document.get("tag")
            if tag not in all_tags:
                all_tags.append(tag)
        try:
            to_clear = set()

            clan_results = clan_feed_db.find()
            l = await clan_feed_db.count_documents(filter={})
            for re in await clan_results.to_list(length=l):
                webhook_id = re.get("webhook")
                thread_id = re.get("thread")
                clan_tag = re.get("clan_tag")
                server_id = re.get("server")

                if webhook_id is None:
                    continue
                try:
                    webhook = await self.bot.fetch_webhook(webhook_id)
                    if thread_id is not None:
                        thread = await self.bot.fetch_channel(thread_id)
                except (disnake.NotFound, disnake.Forbidden):
                    await clan_feed_db.update_one({"server": server_id}, {'$set': {"webhook": None}})
                    await clan_feed_db.update_one({"server": server_id}, {'$set': {"thread": None}})
                    continue
                except Exception as e:
                    c = await self.bot.fetch_channel(923767060977303552)
                    e = str(e)
                    e = e[0:2000]
                    await c.send(content=e)
                    continue

                clan = await getClan(clan_tag)
                if clan is None:
                    continue
                members = clan.members
                member_tags = []
                for member in members:
                    if str(member.league) == "Legend League":
                        member_tags.append(member.tag)

                server_results = await server_db.find_one({"server": server_id})
                server_def = server_results.get("server_def")
                trophy_change_results = ongoing_stats.find({"$and": [
                    {"tag": {"$in": member_tags}},
                    {"new_change": {"$ne": None}}
                ]})
                limit = await ongoing_stats.count_documents(filter={"$and": [
                    {"tag": {"$in": member_tags}},
                    {"new_change": {"$ne": None}}
                ]})

                off_text_changes = []
                def_text_changes = []
                off_cresults = []
                def_cresults = []
                for trophy_change_result in await trophy_change_results.to_list(length=limit):
                    name = trophy_change_result.get("name")
                    tag = trophy_change_result.get("tag")
                    # clan = trophy_change_result.get("clan")
                    link = trophy_change_result.get("link")

                    changes = trophy_change_result.get("new_change")
                    for change in changes:
                        if "<:sword:825589136026501160>" in change:
                            off_text_changes.append(change)
                            off_cresults.append(trophy_change_result)
                        else:
                            def_text_changes.append(change)
                            def_cresults.append(trophy_change_result)

                    # print(off_text_changes)
                    if len(off_text_changes) >= 10:
                        change_text = "\n".join(off_text_changes)
                        embed = disnake.Embed(description=change_text, color=disnake.Color.green())
                        if len(off_cresults) <= 25:
                            components = self.feed_components(off_cresults, "green")
                        else:
                            components = []
                        if thread_id is None:
                            await webhook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url,
                                               components=components)
                        else:
                            await webhook.send(embed=embed, components=components)
                        off_text_changes = []
                        off_cresults = []

                    if len(def_text_changes) >= 10:
                        if server_def == "Off":
                            continue
                        change_text = "\n".join(def_text_changes)
                        embed = disnake.Embed(description=change_text, color=disnake.Color.red())
                        if len(def_cresults) <= 25:
                            components = self.feed_components(def_cresults)
                        else:
                            components = []
                        if thread_id is None:
                            await webhook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url,
                                               components=components)
                        else:
                            await webhook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url,
                                               components=components)
                        def_text_changes = []
                        def_cresults = []

                if len(off_text_changes) > 0:
                    change_text = "\n".join(off_text_changes)
                    embed = disnake.Embed(description=change_text, color=disnake.Color.green())
                    if len(off_cresults) <= 25:
                        components = self.feed_components(off_cresults, "green")
                    else:
                        components = []
                    if thread_id is None:
                        await webhook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url,
                                           components=components)
                    else:
                        await webhook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url,
                                           components=components)

                if len(def_text_changes) > 0:
                    if server_def == "Off":
                        continue
                    change_text = "\n".join(def_text_changes)
                    embed = disnake.Embed(description=change_text, color=disnake.Color.red())
                    if len(def_cresults) <= 25:
                        components = self.feed_components(def_cresults)
                    else:
                        components = []
                    if thread_id is None:
                        await webhook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url,
                                           components=components)
                    else:
                        await webhook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url,
                                           components=components)

                #left over meaning arent tracked
                for tag in member_tags:
                    if tag in all_tags:
                        member_tags.remove(tag)

                async for player in coc_client.get_players(member_tags):
                    try:
                        await addLegendsPlayer_GLOBAL(player, clan.name)
                    except:
                        continue


            server_results = server_db.find()
            limit = await server_db.count_documents(filter={})
            for server_result in await server_results.to_list(length=limit):
                #fetch server's webhook
                webhook_id = server_result.get("webhook")
                server_id = server_result.get("server")
                thread_id = server_result.get("thread")
                if webhook_id is None:
                    continue
                try:
                    webhook = await self.bot.fetch_webhook(webhook_id)
                    if thread_id is not None:
                        thread = await self.bot.fetch_channel(thread_id)
                except (disnake.NotFound, disnake.Forbidden):
                    await server_db.update_one({"server": server_id}, {'$set': {"webhook": None}})
                    await server_db.update_one({"server": server_id}, {'$set': {"thread": None}})
                    continue
                except Exception as e:
                    c = await self.bot.fetch_channel(923767060977303552)
                    e = str(e)
                    e = e[0:2000]
                    await c.send(content=e)
                    continue

                tracked_members = server_result.get("tracked_members")
                server_def = server_result.get("server_def")
                trophy_change_results = ongoing_stats.find({"$and": [
                    {"tag": {"$in": tracked_members}},
                    {"new_change": {"$ne": None}}
                    ]})
                limit = await ongoing_stats.count_documents(filter={"$and": [
                    {"tag": {"$in": tracked_members}},
                    {"new_change": {"$ne": None}}
                    ]})

                off_text_changes = []
                def_text_changes = []
                off_cresults = []
                def_cresults = []
                for trophy_change_result in await trophy_change_results.to_list(length=limit):
                    name = trophy_change_result.get("name")
                    tag = trophy_change_result.get("tag")
                    to_clear.add(tag)
                    #clan = trophy_change_result.get("clan")
                    link = trophy_change_result.get("link")

                    changes = trophy_change_result.get("new_change")
                    for change in changes:
                        if "<:sword:825589136026501160>" in change:
                            off_text_changes.append(change)
                            off_cresults.append(trophy_change_result)
                        else:
                            def_text_changes.append(change)
                            def_cresults.append(trophy_change_result)


                    if len(off_text_changes) >= 10:
                        change_text = "\n".join(off_text_changes)
                        embed = disnake.Embed(description=change_text, color=disnake.Color.green())
                        if len(off_cresults) <= 25:
                            components = self.feed_components(off_cresults, "green")
                        else:
                            components = []
                        if thread_id is None:
                            await webhook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url, components=components)
                        else:
                            await webhook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url, components=components, thread=thread)
                        off_text_changes = []
                        off_cresults = []


                    if len(def_text_changes) >= 10:
                        if server_def == "Off":
                            continue
                        change_text = "\n".join(def_text_changes)
                        embed = disnake.Embed(description=change_text, color=disnake.Color.red())
                        if len(def_cresults)<= 25:
                            components = self.feed_components(def_cresults)
                        else:
                            components = []
                        if thread_id is None:
                            await webhook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url, components=components)
                        else:
                            await webhook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url, components=components, thread=thread)
                        def_text_changes = []
                        def_cresults = []

                if len(off_text_changes) > 0:
                    change_text = "\n".join(off_text_changes)
                    embed = disnake.Embed(description=change_text, color=disnake.Color.green())
                    if len(off_cresults) <= 25:
                        components = self.feed_components(off_cresults, "green")
                    else:
                        components = []
                    if thread_id is None:
                        await webhook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url, components=components)
                    else:
                        await webhook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url, components=components, thread=thread)

                if len(def_text_changes) > 0:
                    if server_def == "Off":
                        continue
                    change_text = "\n".join(def_text_changes)
                    embed = disnake.Embed(description=change_text, color=disnake.Color.red())
                    if len(def_cresults) <= 25:
                        components = self.feed_components(def_cresults)
                    else:
                        components = []
                    if thread_id is None:
                        await webhook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url, components=components)
                    else:
                        await webhook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url, components=components, thread=thread)

                '''
                #keep until we see if it has a use
                dt = datetime.now(utc)
                utc_time = dt.replace(tzinfo=utc)
                utc_timestamp = utc_time.timestamp()
                discord_time = f"<t:{int(utc_timestamp)}:R>"
                '''

            await ongoing_stats.update_many({"tag": {"$in": all_tags}},
                {"$set": {"new_change": []}
                 })
            print("here")
        except Exception as e:
            c = await self.bot.fetch_channel(923767060977303552)
            e = str(e)
            e = e[0:2000]
            await c.send(content=e)


    def feed_components(self, results, color="red"):
        tags=[]
        options = []
        for result in results:
            name = result.get("name")
            trophies = result.get("trophies")
            tag = result.get("tag")
            if tag not in tags:
                tags.append(tag)
                options.append(disnake.SelectOption(label=f"{name} | 🏆{trophies}", value=f"{tag}"))

        stat_select = disnake.ui.Select(
            options=options,
            placeholder="All Stats",
            min_values=1,  # the minimum number of options a user must select
            max_values=1  # the maximum number of options a user can select
        )
        st = disnake.ui.ActionRow()
        st.append_item(stat_select)
        return [st]


    @feed_update.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(LegendsFeed(bot))
