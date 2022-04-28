import re
from coc import utils
from utils.helper import getPlayer, getTags, ongoing_stats, getClan


async def search_results(ctx, query):
    tags = []
    #if search is a player tag, pull stats of the player tag
    if utils.is_valid_tag(query) is True and len(query) >= 5:
        t = utils.correct_tag(tag=query)
        result = await ongoing_stats.find_one({"tag": t})
        if result is not None:
            tags.append(t)
        return tags

    is_discord_id = query.isdigit()
    if is_discord_id:
        ttt = await getTags(ctx, query)
        for tag in ttt:
            result = await ongoing_stats.find_one({"$and": [
            {"tag": tag},
            {"league": {"$eq": "Legend League"}}
            ]})
            if result is not None:
                tags.append(tag)
        if tags != []:
            return tags

    query = query.lower()
    query = re.escape(query)
    results = ongoing_stats.find({"$and" : [
        {"name": {"$regex": f"^(?i).*{query}.*$"}},
        {"league" : {"$eq" : "Legend League"}}
    ]})
    for document in await results.to_list(length=24):
        tags.append(document.get("tag"))
    return tags

async def search_name(query):
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

async def search_name_with_tag(query):
    names = []
    names.append(query)
    #if search is a player tag, pull stats of the player tag

    if utils.is_valid_tag(query) is True:
        t = utils.correct_tag(tag=query)
        query = query.lower()
        query = re.escape(query)
        results = ongoing_stats.find({"$and": [
            {"tag": {"$regex": f"^(?i).*{t}.*$"}}
        ]})
        for document in await results.to_list(length=24):
            names.append(document.get("name") + " | " + document.get("tag"))
        return names

    #ignore capitalization
    #results 3 or larger check for partial match
    #results 2 or shorter must be exact
    #await ongoing_stats.create_index([("name", "text")])

    query = query.lower()
    query = re.escape(query)
    results = ongoing_stats.find({"$and" : [
        {"name": {"$regex": f"^(?i).*{query}.*$"}}
    ]})
    for document in await results.to_list(length=24):
        names.append(document.get("name") + " | " + document.get("tag"))
    return names

async def search_clans_with_tag(query):
    names = set()

    query = re.escape(query)
    results = ongoing_stats.find({"clan": {"$regex": f"^(?i).*{query}.*$"}})
    for document in await results.to_list(length=25):
        names.add(document.get("clan") + " | " + document.get("clan_tag"))
    if list(names) != []:
        return list(names)

    if utils.is_valid_tag(query) is True:
        clan = await getClan(query)
        if clan is None:
            return names
        names.add(clan.name + " | " + clan.tag)
        return list(names)

    return []

async def search_clan_tag(query):

    query = re.escape(query)
    results = ongoing_stats.find({"$and" : [
        {"clan": {"$regex": f"^(?i).*{query}.*$"}},
        {"league" : {"$eq" : "Legend League"}}
    ]})
    for document in await results.to_list(length=1):
        tag = document.get("tag")
        player = await getPlayer(tag)
        clan = await player.get_detailed_clan()
        return clan

    if utils.is_valid_tag(query) is True:
        clan = await getClan(query)
        if clan is None:
            return None
        return clan

    return None

