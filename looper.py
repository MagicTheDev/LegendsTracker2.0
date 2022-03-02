import coc
import asyncio
from datetime import datetime
import time
import os
import motor.motor_asyncio
from dotenv import load_dotenv
load_dotenv()

COC_EMAIL = os.getenv("LOOPER_COC_EMAIL")
COC_PASSWORD = os.getenv("LOOPER_COC_PASSWORD")
DB_LOGIN = os.getenv("DB_LOGIN")

coc_client_two = coc.login(COC_EMAIL, COC_PASSWORD, client=coc.EventsClient, key_names="DiscordBot",
                           key_count=10, throttle_limit=25)


client = motor.motor_asyncio.AsyncIOMotorClient(DB_LOGIN)

ongoing_db = client.legends_stats
ongoing_stats = ongoing_db.ongoing_stats

tags = client.clan_tags
clan_tags = tags.tags_db

moved = False


async def stats_update():
    now = datetime.utcnow()
    hour = str(now.hour)
    minute = now.minute

    global moved
    if (hour == "4") and (minute >= 50) and (moved == True):
        moved = False

    if (hour == "5") and (minute >= 3) and (minute <= 8) and (moved == False):
        await moveStats()
        moved = True

    tags = []
    tracked = ongoing_stats.find()

    # await ongoing_stats.create_index([("tag", 1)], unique = True)

    limit = await ongoing_stats.count_documents(filter={})
    # print(f"Loop 1 size {limit}")
    for document in await tracked.to_list(length=limit):
        tag = document.get("tag")
        if tag not in tags:
            tags.append(tag)

    w = 0
    rtime = time.time()
    #print(f"{len(tags)} player tags")

    average_time = 0
    loops = 0
    went_thru = tags
    async for clash_player in coc_client_two.get_players(tags):
        if w == 0:
            w += 1
            print(time.time() - rtime)

        player = await ongoing_stats.find_one({"tag": f"{clash_player.tag}"})
        if player is None:
            continue

        went_thru.remove(clash_player.tag)

        player_name = player.get("name")
        prev_trophies = int(player.get("trophies"))
        prev_clan = player.get("clan")
        prev_league = player.get("league")

        current_trophies = clash_player.trophies
        current_hits = clash_player.attack_wins
        current_defenses = clash_player.defense_wins

        current_clan = "No Clan"
        try:
            current_clan = clash_player.clan.name
        except:
            pass

        if clash_player.name != player_name:
            await ongoing_stats.update_one({'tag': f"{clash_player.tag}"}, {'$set': {'name': f'{clash_player.name}'}})

        if current_clan != prev_clan:
            await ongoing_stats.update_one({'tag': f"{clash_player.tag}"}, {'$set': {'clan': f'{current_clan}'}})

        if str(clash_player.league) != prev_league:
            await ongoing_stats.update_one({'tag': f"{clash_player.tag}"},
                                           {'$set': {'league': str(clash_player.league)}})

        if int(current_trophies) <= 4700:
            continue

        if str(clash_player.league) != prev_league:
            await ongoing_stats.update_one({'tag': f"{clash_player.tag}"},
                                           {'$set': {'league': f'{str(clash_player.league)}'}})

        prev_def = player.get("num_season_defenses")
        curr_def = clash_player.defense_wins

        if prev_def != curr_def:
            await ongoing_stats.update_one({'tag': f"{clash_player.tag}"},
                                           {'$set': {'num_season_defenses': clash_player.defense_wins}})

            await ongoing_stats.update_one({'tag': f"{clash_player.tag}"},
                                           {'$push': {'today_defenses': 0}})

            await ongoing_stats.update_one({'tag': f"{clash_player.tag}"},
                                           {'$set': {
                                               'change': f"<:clash:877681427129458739> -{str(0)} trophies | <:legends:881450752109850635> {str(current_trophies)}"}})

        if current_trophies != prev_trophies:
            # went negative
            if current_trophies < prev_trophies:

                await ongoing_stats.update_one({'tag': f"{clash_player.tag}"},
                                               {'$set': {'trophies': current_trophies,
                                                         "num_season_hits": clash_player.attack_wins,
                                                         "num_season_defenses": clash_player.defense_wins}})


                await ongoing_stats.update_one({'tag': f"{clash_player.tag}"},
                                               {'$push': {'today_defenses': (prev_trophies - current_trophies)}})

                await ongoing_stats.update_one({'tag': f"{clash_player.tag}"},
                                               {'$set': {
                                                   'change': f"<:clash:877681427129458739> -{str(prev_trophies - current_trophies)} trophies | <:legends:881450752109850635> {str(current_trophies)}"}})


            # went positive
            elif current_trophies > prev_trophies:

                seasonHits = int(player.get("num_season_hits"))
                change = current_trophies - prev_trophies
                diffHits = clash_player.attack_wins - seasonHits

                # print(f"tag : {clash_player.tag}"
                # f"season hits : {seasonHits}\n"
                #  f"change : {change}\n"
                #  f"diffhits : {diffHits}" )

                multipleTriples = False
                if diffHits >= 2 and change % 40 == 0:
                    multipleTriples = True
                    for x in range(0, diffHits):
                        await ongoing_stats.update_one({'tag': f"{clash_player.tag}"},
                                                       {'$push': {
                                                           'today_hits': 40}})
                        await ongoing_stats.update_one({'tag': f"{clash_player.tag}"},
                                                       {'$inc': {'num_today_hits': 1}})
                        await ongoing_stats.update_one({'tag': f"{clash_player.tag}"},
                                                       {'$inc': {'row_triple': 1}})
                else:
                    await ongoing_stats.update_one({'tag': f"{clash_player.tag}"},
                                                   {'$push': {
                                                       'today_hits': (current_trophies - prev_trophies)}})
                    for x in range(0, diffHits):
                        await ongoing_stats.update_one({'tag': f"{clash_player.tag}"},
                                                       {'$inc': {'num_today_hits': 1}})
                    if diffHits == 1 and change == 40:
                        await ongoing_stats.update_one({'tag': f"{clash_player.tag}"},
                                                       {'$inc': {'row_triple': 1}})
                    else:
                        await ongoing_stats.update_one({'tag': f"{clash_player.tag}"},
                                                       {'$set': {'row_triple': 0}})

                results = await ongoing_stats.find_one({"tag": f"{clash_player.tag}"})
                numberOfTriples = results.get("row_triple")
                highest_streak = results.get("highest_streak")
                if highest_streak == None:
                    highest_streak = 0
                if numberOfTriples > highest_streak:
                    await ongoing_stats.update_one({'tag': f"{clash_player.tag}"},
                                                   {'$set': {'highest_streak': numberOfTriples}})

                attacksText = ""
                onfire = ""

                if numberOfTriples >= 2:
                    onfire = f"\nOn fire 🔥 {numberOfTriples} triples in a row 🔥"

                if multipleTriples == True:
                    hits = results.get("today_hits")
                    for x in range(1, diffHits + 1):
                        thisHit = hits[-x]
                        attacksText += f"<:sword:825589136026501160> +{thisHit} trophies"
                else:
                    if diffHits >= 2:
                        attacksText += f"<:sword:825589136026501160> `x{diffHits}`: +{change} trophies"
                    else:
                        attacksText += f"<:sword:825589136026501160> +{change} trophies"

                await ongoing_stats.update_one({'tag': f"{clash_player.tag}"},
                                               {'$set': {
                                                   'change': f"{attacksText} | <:legends:881450752109850635> {str(current_trophies)}{onfire}"
                                               }})

            await ongoing_stats.update_one({'tag': f"{clash_player.tag}"},
                                           {'$set': {'trophies': current_trophies,
                                                     "num_season_hits": clash_player.attack_wins}})

    removed = []
    for t in went_thru:
        try:
            await coc_client_two.get_player(player_tag=t)
        except coc.Maintenance:
            continue
        except coc.NotFound:
            await ongoing_stats.delete_one({'tag': f"{t}"})
            removed.append(t)
        except:
            continue

    if removed != []:
        print(f"Removed: {removed}")
    print(f"Loop 3: {time.time() - rtime}")
    await asyncio.sleep(5)

async def moveStats():
    tracked = ongoing_stats.find()
    limit = await ongoing_stats.count_documents(filter={})
    for document in await tracked.to_list(length=limit):
        tag = document.get("tag")
        today_hits = document.get("today_hits")
        today_defenses = document.get("today_defenses")
        num_today_hits = document.get("num_today_hits")
        trophies = document.get("trophies")

        await ongoing_stats.update_one({'tag': f"{tag}"},
                                       {'$set': {"num_yesterday_hits": num_today_hits,
                                                 "today_hits": [],
                                                 "num_today_hits": 0,
                                                 "today_defenses": []}})
        await ongoing_stats.update_one({'tag': f"{tag}"},
                                       {'$push': {"end_of_day": trophies,
                                                  "previous_hits": today_hits,
                                                  "previous_defenses": today_defenses}})

    print("Stats Shifted & Stored")

@coc.ClientEvents.new_season_start()
async def new_Season():
    await asyncio.sleep(300)
    tracked = ongoing_stats.find()
    limit = await ongoing_stats.count_documents(filter={})
    for document in await tracked.to_list(length=limit):
        tag = document.get("tag")
        await ongoing_stats.update_one({'tag': f"{tag}"},
                                       {'$set': {"trophies": 5000,
                                                 "num_season_hits": 0,
                                                 "num_season_defenses": 0}})


while True:
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(stats_update())
    except:
        continue


