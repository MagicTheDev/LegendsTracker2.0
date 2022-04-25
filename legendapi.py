from typing import Optional
import motor.motor_asyncio
import uvicorn
from datetime import datetime
import pytz
utc = pytz.utc
from coc import utils
import coc

from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
from dotenv import load_dotenv
load_dotenv()

DB_LOGIN = os.getenv("DB_LOGIN")
COC_EMAIL = os.getenv("BETA_COC_EMAIL")
COC_PASSWORD = os.getenv("BETA_COC_PASSWORD")
from utils.helper import coc_client
db_client = motor.motor_asyncio.AsyncIOMotorClient(DB_LOGIN)
legends_stats = db_client.legends_stats
ongoing_stats = legends_stats.ongoing_stats
logins = legends_stats.logins

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(token, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user



@app.get("/player/{player_tag}")
@limiter.limit("60/second")
async def player(player_tag: str, request : Request, response: Response):
    player_tag = utils.correct_tag(player_tag)
    result = await ongoing_stats.find_one({"tag": player_tag})

    if result is None:
        raise HTTPException(status_code=404, detail="Item not found")
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
    clan_tag = result.get("clan_tag")
    th = result.get("th")
    clan_badge = result.get("badge")
    player_link = result.get("link")
    location = result.get("location")
    if location is None:
        location = "Unknown"

    season_stats = season_hit_stats(result)

    return{
        "name" : name,
        "tag" : tag,
        "player_link" : player_link,
        "location" : location,
        "clan" : clan,
        "clan_tag" : clan_tag,
        "clan_badge" : clan_badge,
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
        "end_of_days" : end_of_days,
        "offense_season_one_star_average" : season_stats[0],
        "offense_season_two_star_average"  :season_stats[1],
        "offense_season_three_star_average" : season_stats[2],
        "defense_season_one_star_average" : season_stats[3],
        "defense_season_two_star_average" : season_stats[4],
        "defense_season_three_star_average" : season_stats[5],
        "season_average_offense" : season_stats[6],
        "season_average_defense" : season_stats[7],
        "season_average_net" : season_stats[8],
        "num_prev_season_days_tracked" : season_stats[11]
    }

@app.post("/add/{player_tag}")
@limiter.limit("10/second")
async def player_add(player_tag: str, request : Request, response: Response):
        try:
            player = await coc_client.get_player(player_tag)
        except:
            raise HTTPException(status_code=404, detail="Invalid Player")

        if str(player.league) != "Legend League":
            raise HTTPException(status_code=404, detail="Cannot add players not in legends")

        result = await ongoing_stats.find_one({"tag": player.tag})
        if result is not None:
            raise HTTPException(status_code=404, detail="Player already added")

        clan_name = "No Clan"

        if player.clan is not None:
            clan_name = player.clan.name

        if player.clan is not None:
            badge = player.clan.badge.url
        else:
            badge = clan_name
        await ongoing_stats.insert_one({
            "tag": player.tag,
            "name": player.name,
            "trophies": player.trophies,
            "th": 14,
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
            "badge": badge,
            "link": player.share_link,
            "league": str(player.league),
            "highest_streak": 0,
            "last_updated": None,
            "change": None
        })

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

def season_hit_stats(player):
    start = utils.get_season_start().replace(tzinfo=utc).date()
    now = datetime.utcnow().replace(tzinfo=utc).date()
    now_ = datetime.utcnow().replace(tzinfo=utc)
    current_season_progress = now - start
    current_season_progress = current_season_progress.days
    if now_.hour <= 5:
        current_season_progress -= 1
    first_record = 0
    last_record = current_season_progress
    y = player.get("end_of_day")

    len_y = len(y)
    if last_record == len_y:
        last_record -= 1
    if last_record > len_y:
        last_record = len(y) - 1

    if first_record >= len_y - 2:
        return [0, 0, 0, 0, 0,
                0, None, None, None, 0, 0, 0]

    one_stars = 0
    two_stars = 0
    three_stars = 0

    zero_star_def = 0
    one_stars_def = 0
    two_stars_def = 0
    three_stars_def = 0

    hits = player.get("previous_hits")
    defs = player.get("previous_defenses")
    hits = hits[len(hits) - last_record:len(hits) - first_record]
    defs = defs[len(defs) - last_record:len(defs) - first_record]
    length = len(hits)

    l_hit = 0
    sum_hits = 0
    for day in hits:
        if len(day) >= 6:
            sum_hits += sum(day)
            l_hit += 1
        for hit in day:
            if hit >= 5 and hit <= 15:
                one_stars += 1
            elif hit >= 16 and hit <= 32:
                two_stars += 1
            elif hit >= 40:
                if hit % 40 == 0:
                    three_stars += (hit // 40)

    total = one_stars + two_stars + three_stars
    try:
        one_stars_avg = int(round((one_stars / total), 2) * 100)
    except:
        one_stars_avg = 0
    try:
        two_stars_avg = int(round((two_stars / total), 2) * 100)
    except:
        two_stars_avg = 0
    try:
        three_stars_avg = int(round((three_stars / total), 2) * 100)
    except:
        three_stars_avg = 0

    l_defs = 0
    sum_defs = 0
    for day in defs:
        if len(day) >= 6:
            sum_defs += sum(day)
            l_defs+=1
        for hit in day:
            if hit >= 0 and hit <= 4:
                zero_star_def += 1
            if hit >= 5 and hit <= 15:
                one_stars_def += 1
            elif hit >= 16 and hit <= 32:
                two_stars_def += 1
            elif hit >= 40:
                if hit % 40 == 0:
                    three_stars_def += (hit // 40)

    total_def = zero_star_def + one_stars_def + two_stars_def + three_stars_def
    try:
        zero_stars_avg_def = int(round((zero_star_def / total_def), 2) * 100)
    except:
        zero_stars_avg_def = 0
    try:
        one_stars_avg_def = int(round((one_stars_def / total_def), 2) * 100)
    except:
        one_stars_avg_def = 0
    try:
        two_stars_avg_def = int(round((two_stars_def / total_def), 2) * 100)
    except:
        two_stars_avg_def = 0
    try:
        three_stars_avg_def = int(round((three_stars_def / total_def), 2) * 100)
    except:
        three_stars_avg_def = 0

    if l_hit == 0:
        average_offense = l_hit
    else:
        average_offense = int(sum_hits/l_hit)

    if l_defs == 0:
        average_defense = l_defs
    else:
        average_defense = int(sum_defs/l_defs)
    average_net = average_offense - average_defense

    return [one_stars_avg, two_stars_avg, three_stars_avg, one_stars_avg_def, two_stars_avg_def,
            three_stars_avg_def, average_offense, average_defense, average_net, len(hits), len(defs), length]





if __name__ == '__main__':
    uvicorn.run("legendapi:app", port=8000, host='45.33.3.218')
