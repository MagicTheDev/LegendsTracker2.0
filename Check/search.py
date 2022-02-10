import re

from discord.ext import commands
from helper import getPlayer, getTags, ongoing_stats


class search(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    async def search_results(self, ctx, query):
        tags = []
        #if search is a player tag, pull stats of the player tag
        player = await getPlayer(query)
        if player is not None:
            result = await ongoing_stats.find_one({"tag": player.tag})
            if result is not None:
                tags.append(player.tag)
            return tags


        ttt = await getTags(ctx, query)
        for tag in ttt:
            result = await ongoing_stats.find_one({"tag": tag})
            if result is not None:
                tags.append(tag)
        if tags != []:
            return tags


        #ignore capitalization
        #results 3 or larger check for partial match
        #results 2 or shorter must be exact
        #await ongoing_stats.create_index([("name", "text")])

        query = query.lower()
        query = re.escape(query)
        results = ongoing_stats.find({"$and" : [
            {"name": {"$regex": f"^(?i).*{query}.*$"}},
            {"league" : {"$eq" : "Legend League"}}
        ]})
        for document in await results.to_list(length=25):
            tags.append(document.get("tag"))
        return tags


def setup(bot: commands.Bot):
    bot.add_cog(search(bot))