import coc
import asyncio
from datetime import datetime
import time
import os
import motor.motor_asyncio
from dotenv import load_dotenv
load_dotenv()
from customplayer import CustomPlayer
SUPER_SCRIPTS=["⁰","¹","²","³","⁴","⁵","⁶", "⁷","⁸", "⁹"]

COC_EMAIL = os.getenv("LOOPER_COC_EMAIL")
COC_PASSWORD = os.getenv("LOOPER_COC_PASSWORD")
DB_LOGIN = os.getenv("DB_LOGIN")

coc_client_two = coc.login(COC_EMAIL, COC_PASSWORD, client=coc.EventsClient, key_names="Test",
                           key_count=10, throttle_limit=25, cache_max_size=None)

client = motor.motor_asyncio.AsyncIOMotorClient(DB_LOGIN)

ongoing_db = client.legends_stats
ongoing_stats = ongoing_db.ongoing_stats

moved = True

async def stats_update():

    #Check & Start for EOS & EOD Movements
    now = datetime.utcnow()
    hour = str(now.hour)
    minute = now.minute
    global moved
    if (hour == "4") and (minute >= 50) and (moved is True):
        moved = False

    if (hour == "5") and (minute >= 3) and (minute <= 8) and (moved is False):
        await moveStats()
        moved = True


    #retrieve all tags
    tags = []
    tracked = ongoing_stats.find()
    limit = await ongoing_stats.count_documents(filter={})
    for document in await tracked.to_list(length=limit):
        tag = document.get("tag")
        if tag not in tags:
            tags.append(tag)
        #if len(tags) == 20:
            #break

    iterations = 0
    rtime = time.time()
    went_thru = tags
    async for player in coc_client_two.get_players(tags, cls=CustomPlayer):
        if iterations == 0:
            iterations += 1
            #time to fetch all tags
            print(time.time() - rtime)

        player: CustomPlayer
        result = await ongoing_stats.find_one({"tag": player.tag})
        went_thru.remove(player.tag)

        await player.update_name(result)
        await player.update_league(result)
        await player.update_clan_name(result)
        await player.update_clan_badge(result)
        await player.update_th(result)
        await player.update_clan_tag(result)

        if player.is_legend() is False:
            await player.update_trophies(result)
            await player.set_season_hits()
            continue

        trophies_changed = player.trophies_changed(result)

        if trophies_changed is not None:
            await player.set_last_update()
            # went negative
            if trophies_changed<= -1:
                await player.update_trophies(result)
                await ongoing_stats.update_one({'tag': f"{player.tag}"},
                                               {'$push': {'today_defenses': abs(trophies_changed)}})

                await ongoing_stats.update_one({'tag': f"{player.tag}"},
                                               {'$push': {
                                                   'new_change': f"<:clash:877681427129458739> -{abs(trophies_changed)} | <:legends:881450752109850635>{player.trophies} | {player.name}"}})

            # went positive
            elif trophies_changed>= 1:
                diff_hits = player.attack_wins - player.db_season_hits(result)

                multipleTriples = False
                number_of_triples = 0
                if diff_hits >= 2 and trophies_changed % 40 == 0:
                    multipleTriples = True
                    for x in range(0, diff_hits):
                        await player.insert_attack(40)
                        await player.increment_todays_hits()
                        await player.increment_streak()
                        number_of_triples+=1
                else:
                    await player.update_trophies(result)
                    for x in range(0, diff_hits):
                        await player.increment_todays_hits()
                    if diff_hits == 1 and trophies_changed == 40:
                        await player.increment_streak()
                    else:
                        await player.reset_streak()

                current_streak = await player.db_current_streak()
                highest_streak = player.db_highest_streak(result)
                if current_streak > highest_streak:
                    await player.update_highest_streak()

                attacksText = ""
                onfire = ""

                if number_of_triples >= 2:
                    onfire = f"| 🔥 `x{number_of_triples}`"

                if multipleTriples is True:
                    hits = await player.get_todays_hits()
                    for x in range(1, diff_hits + 1):
                        thisHit = hits[-x]
                        attacksText += f"<:sword:825589136026501160> +{thisHit}"
                        await ongoing_stats.update_one({'tag': f"{player.tag}"},
                                                       {'$push': {
                                                           'new_change': f"{attacksText} | <:legends:881450752109850635>{str(player.trophies)}{onfire} | {player.name}"
                                                       }})
                else:
                    if diff_hits >= 2:
                        s = SUPER_SCRIPTS[diff_hits]
                        attacksText += f"<:sword:825589136026501160> +{trophies_changed}{s}"
                    else:
                        attacksText += f"<:sword:825589136026501160> +{trophies_changed}"

                    await player.insert_attack(trophies_changed)
                    await ongoing_stats.update_one({'tag': f"{player.tag}"},
                                                   {'$push': {
                                                       'new_change': f"{attacksText} | <:legends:881450752109850635>{str(player.trophies)}{onfire} | {player.name}"
                                                   }})


            await ongoing_stats.update_one({'tag': f"{player.tag}"},
                                           {'$set': {'trophies': player.trophies,
                                                     "num_season_hits": player.attack_wins}})

        if player.db_season_defs(result) != player.defense_wins:
            await ongoing_stats.update_one({'tag': f"{player.tag}"},
                                           {'$set': {'num_season_defenses': player.defense_wins}})

            await player.insert_defense(0)

            await ongoing_stats.update_one({'tag': f"{player.tag}"},
                                           {'$push': {
                                               'new_change': f"<:clash:877681427129458739> -{str(0)} | <:legends:881450752109850635>{str(player.trophies)} | {player.name}"}})

            await player.set_last_update()

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
    print(f"Loop : {time.time() - rtime}")
    cache = coc_client_two.http.cache
    #print("cache length: " + str(len(cache)))
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
    except Exception as e:
        print(e)
        pass



