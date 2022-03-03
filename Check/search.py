import re
from coc import utils
from disnake.ext import commands
from helper import getPlayer, getTags, ongoing_stats, getClan


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

    async def search_name(self, query):
        names = []
        #if search is a player tag, pull stats of the player tag

        if utils.is_valid_tag(query) is True:
            t = utils.correct_tag(tag=query)
            query = query.lower()
            query = re.escape(query)
            results = ongoing_stats.find({"$and": [
                {"tag": {"$regex": f"^(?i).*{t}.*$"}},
                {"league": {"$eq": "Legend League"}}
            ]})
            for document in await results.to_list(length=25):
                names.append(document.get("name"))
            return names



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
            names.append(document.get("name"))
        return names

    async def search_clans(self, query):
        names = []

        query = re.escape(query)
        results = ongoing_stats.find({"clan": {"$regex": f"^(?i).*{query}.*$"}})
        found = 0
        limit = await ongoing_stats.count_documents(filter={"clan": {"$regex": f"^(?i).*{query}.*$"}})
        for document in await results.to_list(length=limit):
            c = document.get("clan")
            if c not in names:
                found += 1
                names.append(c)
            if found == 25:
                return names
        if names != []:
            return names

        if utils.is_valid_tag(query) is True:
            clan = await getClan(query)
            if clan is None:
                return names
            names.append(clan.name)
            return names

        return names

    async def search_clan_tag(self, query):

        query = re.escape(query)
        results = ongoing_stats.find({"$and" : [
            {"clan": {"$regex": f"^(?i).*{query}.*$"}},
            {"league" : {"$eq" : "Legend League"}}
        ]})
        for document in await results.to_list(length=1):
            tag = document.get("tag")
            player = await getPlayer(tag)
            return player.clan

        if utils.is_valid_tag(query) is True:
            clan = await getClan(query)
            if clan is None:
                return None
            return clan

        return None

def setup(bot: commands.Bot):
    bot.add_cog(search(bot))