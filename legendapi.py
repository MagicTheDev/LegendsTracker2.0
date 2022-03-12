from typing import Optional
import motor.motor_asyncio
import uvicorn

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
    user = get_user(fake_users_db, token)
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


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


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
    uvicorn.run("legendapi:app", port=8000, host='45.33.3.218')
