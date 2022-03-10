from utils.helper import ongoing_stats, server_db

async def addLegendsPlayer_GLOBAL(player, clan_name):
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
        "servers": [],
        "end_of_day": [],
        "clan": clan_name,
        "link": player.share_link,
        "league": str(player.league),
        "highest_streak": 0,
        "last_updated": None,
        "change": None
    })


async def addLegendsPlayer_SERVER(guild_id, player):
    await ongoing_stats.update_one({'tag': player.tag},
                                   {'$push': {"servers": guild_id}})
    await server_db.update_one({'server': guild_id},
                               {'$push': {"tracked_members": player.tag}})


async def removeLegendsPlayer_SERVER(guild_id, player):
    await ongoing_stats.update_one({'tag': player.tag},
                                   {'$pull': {"servers": guild_id}})
    await server_db.update_one({'server': guild_id},
                               {'$pull': {"tracked_members": player.tag}})


async def check_global_tracked(player):
    results = await ongoing_stats.find_one({"tag": f"{player.tag}"})
    return results != None

async def check_server_tracked(player, server_id):
    results = await server_db.find_one({"server": server_id})
    tracked_members = results.get("tracked_members")

    results = await ongoing_stats.find_one({"tag": player.tag})
    if results != None:
        servers = []
        servers = results.get("servers")
        if servers == None:
            servers = []
    else:
        servers = []

    return ((player.tag in tracked_members) or (server_id in servers))