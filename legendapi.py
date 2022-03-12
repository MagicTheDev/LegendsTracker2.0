from typing import Optional
import motor.motor_asyncio
import uvicorn

from fastapi import FastAPI, Request, Response

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
from dotenv import load_dotenv
load_dotenv()


DB_LOGIN = os.getenv("DB_LOGIN")

db_client = motor.motor_asyncio.AsyncIOMotorClient(DB_LOGIN)
legends_stats = db_client.legends_stats
ongoing_stats = legends_stats.ongoing_stats

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/player/{player_tag}")
@limiter.limit("60/second")
async def player(player_tag: str, request : Request, response: Response):
    result = await ongoing_stats.find_one({"tag": player_tag})
    name = result.get("name")
    tag = result.get("tag")
    clan = result.get("clan")
    league = result.get("league")
    trophies = result.get("trophies")
    num_season_hits = result.get("num_season_hits")
    streak = result.get("row_triple")
    todays_hits = result.get("today_hits")
    todays_defs = result.get("today_defenses")
    num_today_hits = result.get("num_today_hits")
    num_yesterday_hits = result.get("num_yesterday_hits")
    previous_hits = result.get("previous_hits")
    previous_defs = result.get("previous_defenses")
    end_of_days = result.get("end_of_day")
    highest_streak = result.get("highest_streak")

    return{
        "name" : name,
        "tag" : tag,
        "clan" : clan,
        "trophies" : trophies,
        "league" : league,
        "num_season_hits" : num_season_hits,
        "current_streak" : streak,
        "highest_streak": highest_streak,
        "todays_hits" : todays_hits,
        "todays_defs" : todays_defs,
        "num_today_hits" : num_today_hits,
        "num_yesterday_hits":num_yesterday_hits,
        "previous_hits" : previous_hits,
        "previous_defs" : previous_defs,
        "end_of_days" : end_of_days
    }

@app.get("/all_tags")
@limiter.limit("10/minute")
async def all_tags(request : Request, response: Response):
    tags = []
    tracked = ongoing_stats.find({"league" : {"$eq" : "Legend League"}})
    limit = await ongoing_stats.count_documents(filter={"league" : {"$eq" : "Legend League"}})
    for document in await tracked.to_list(length=limit):
        tag = document.get("tag")
        if tag not in tags:
            tags.append(tag)
    return tags

@app.get("/ordered_tags")
@limiter.limit("10/minute")
async def _ordered(request : Request, response: Response):
    tags = []
    tracked = ongoing_stats.find({"league" : {"$eq" : "Legend League"}}).sort("trophies", -1)
    limit = await ongoing_stats.count_documents(filter={"league" : {"$eq" : "Legend League"}})
    for document in await tracked.to_list(length=limit):
        tag = document.get("tag")
        if tag not in tags:
            tags.append(tag)
    return tags

if __name__ == '__main__':
    uvicorn.run("legendapi:app", port=80, host='45.33.3.218')
