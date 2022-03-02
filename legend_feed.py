
import disnake
from disnake.ext import commands, tasks
import aiohttp
from datetime import datetime
import pytz
utc = pytz.utc
from disnake import Webhook
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
        webhooks = {}

        for feed in await tracked.to_list(length=limit):
            webhook = feed.get("webhook")
            server = feed.get("server")
            thread = feed.get("thread")
            if webhook is None:
                continue
            try:
                webhook = await self.bot.fetch_webhook(webhook)
                if thread is not None:
                    thread = await self.bot.fetch_channel(thread)
            except disnake.NotFound:
                await server_db.update_one({"server": server}, {'$set': {"webhook": None}})
                await server_db.update_one({"server": server}, {'$set': {"thread": None}})
                continue

            if webhook is not None:
                webhooks[server] = webhook
                webhooks[webhook] = thread



        tracked = ongoing_stats.find({"change": {"$ne" : None}})
        limit = await ongoing_stats.count_documents(filter={"change": {"$ne" : None}})

        dt = datetime.now(utc)
        utc_time = dt.replace(tzinfo=utc)
        utc_timestamp = utc_time.timestamp()
        discord_time = f"<t:{int(utc_timestamp)}:R>"



        for document in await tracked.to_list(length=limit):
            servers = document.get("servers")
            if servers == None:
                continue

            change = document.get("change")
            tag = document.get("tag")
            name = document.get("name")
            clan = document.get("clan")
            link = document.get("link")
            change = str(change)

            for server in servers:
                webhook = webhooks.get(server)
                thread = webhooks.get(webhook)

                if webhook is None:
                    continue

                if "Defense Won" in change:
                    color = disnake.Color.green()
                    button_color = disnake.ButtonStyle.green
                elif "Defense" in change:
                    color = disnake.Color.red()
                    button_color = disnake.ButtonStyle.red
                else:
                    color = disnake.Color.green()
                    button_color = disnake.ButtonStyle.green
                embed = disnake.Embed(title=f"{name} | {clan}",
                                      description=change + f"{discord_time} | [profile]({link})",
                                      color=color)
                embed.set_footer(text=f"{tag}")

                button = disnake.ui.Button(label="All Stats", emoji="📊", style=button_color, custom_id=f"{tag}")
                buttons = disnake.ui.ActionRow()
                buttons.append_item(button)
                print(webhook)
                print(server)

                if thread is not None:
                    await webhook.send(embed=embed,  components=[buttons], username='Legends Tracker',
                                   avatar_url="https://cdn.discordapp.com/attachments/843624785560993833/938961364100190269/796f92a51db491f498f6c76fea759651_1.png", thread=thread)
                else:
                    await webhook.send(embed=embed, components=[buttons], username='Legends Tracker',
                                       avatar_url="https://cdn.discordapp.com/attachments/843624785560993833/938961364100190269/796f92a51db491f498f6c76fea759651_1.png")

                await ongoing_stats.update_one({'tag': tag},
                                       {'$set': {'change': None}})


    @feed_update.before_loop
    async def before_printer(self):
        print('waiting...')
        await self.bot.wait_until_ready()




def setup(bot: commands.Bot):
    bot.add_cog(legends_feed(bot))