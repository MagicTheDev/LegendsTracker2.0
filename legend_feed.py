
import discord
from discord.ext import commands, tasks



from datetime import datetime
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component
from discord_slash.model import ButtonStyle
import pytz
utc = pytz.utc

from helper import server_db, ongoing_stats



class legends_feed(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.feed_update.start()


    def cog_unload(self):
        self.feed_update.cancel()


    @tasks.loop(seconds=10)
    async def feed_update(self):
        tracked = server_db.find()
        limit = await server_db.count_documents(filter={})

        channels = []
        for feed in await tracked.to_list(length=limit):
            channel = feed.get("channel_id")
            server = feed.get("server")
            if channel is not None:
                try:
                    channel = await self.bot.fetch_channel(channel)
                    # print(channel.name)
                    channels.append(server)
                    channels.append(channel)
                except discord.NotFound:
                    tracked = ongoing_stats.find({})
                    limit = await ongoing_stats.count_documents(filter={})
                    for document in await tracked.to_list(length=limit):
                        servers = document.get("servers")
                        if servers == None:
                            continue
                        if server in servers:
                            tag = document.get("tag")
                            print(tag)
                            await ongoing_stats.update_one({'tag': f"{tag}"},
                                                           {'$pull': {'servers': server}})
                    await server_db.update_one({"channel_id": channel}, {'$set': {"channel_id": None}})
                except discord.Forbidden:
                    tracked = ongoing_stats.find({})
                    limit = await ongoing_stats.count_documents(filter={})
                    for document in await tracked.to_list(length=limit):
                        servers = document.get("servers")
                        if servers == None:
                            continue
                        if server in servers:
                            tag = document.get("tag")
                            print(tag)
                            await ongoing_stats.update_one({'tag': f"{tag}"},
                                                           {'$pull': {'servers': server}})
                    await server_db.update_one({"channel_id": channel}, {'$set': {"channel_id": None}})
                except Exception as e:
                    print(e)
                    channel = await self.bot.fetch_channel(923767060977303552)
                    await channel.send(f"{e}")


        tracked = ongoing_stats.find({"change": {"$ne" : None}})
        limit = await ongoing_stats.count_documents(filter={"change": {"$ne" : None}})

        dt = datetime.now(utc)
        utc_time = dt.replace(tzinfo=utc)
        utc_timestamp = utc_time.timestamp()
        discord_time = f"<t:{int(utc_timestamp)}:R>"


        for document in await tracked.to_list(length=limit):
            change = document.get("change")
            tag = document.get("tag")
            name = document.get("name")
            clan = document.get("clan")
            link = document.get("link")

            change = str(change)
            if change != "None":
                servers = document.get("servers")
                if servers == None:
                    continue
                for server in servers:
                    # print("here")
                    if server in channels:
                        # print("here2")
                        index = channels.index(server)
                        channel = channels[index + 1]
                        color = None
                        if "Defense Won" in change:
                            color = discord.Color.green()
                        elif "Defense" in change:
                            color = discord.Color.red()
                        else:
                            color = discord.Color.green()
                        embed = discord.Embed(title=f"{name} | {clan}",
                                              description=change + f"{discord_time} | [profile]({link})",
                                              color=color)
                        embed.set_footer(text=f"{tag}")
                        # print("here")

                        page_buttons = [
                            create_button(label="All Stats", emoji="📊", style=ButtonStyle.blue,
                                          custom_id=f"{tag}")]
                        page_buttons = create_actionrow(*page_buttons)

                        # print("here")
                        await channel.send(embed=embed, components=[page_buttons])
                        # await asyncio.sleep(0.5)


                await ongoing_stats.update_one({'tag': tag},
                                               {'$set': {'change': None}})


    @feed_update.before_loop
    async def before_printer(self):
        print('waiting...')
        await self.bot.wait_until_ready()




def setup(bot: commands.Bot):
    bot.add_cog(legends_feed(bot))