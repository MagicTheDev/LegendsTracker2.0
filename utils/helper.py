import os
import coc
from coc.ext import discordlinks
import motor.motor_asyncio
from dotenv import load_dotenv
import aiohttp
import operator
IS_BETA = False

load_dotenv()

if not IS_BETA:
    COC_EMAIL = os.getenv("COC_EMAIL")
    COC_PASSWORD = os.getenv("COC_PASSWORD")
    DB_LOGIN = os.getenv("DB_LOGIN")
else:
    COC_EMAIL = os.getenv("BETA_COC_EMAIL")
    COC_PASSWORD = os.getenv("BETA_COC_PASSWORD")
    DB_LOGIN = os.getenv("BETA_DB_LOGIN")

LINK_API_USER = os.getenv("LINK_API_USER")
LINK_API_PW = os.getenv("LINK_API_PW")
PATREON_BEARER = os.getenv("PATREON_BEARER")


coc_client = coc.login(COC_EMAIL, COC_PASSWORD, client=coc.EventsClient, key_count=10, key_names="DiscordBot", throttle_limit = 25)
link_client = discordlinks.login(LINK_API_USER, LINK_API_PW)

db_client = motor.motor_asyncio.AsyncIOMotorClient(DB_LOGIN)

if not IS_BETA:
    #### DATABASES USED ####
    legends_stats = db_client.legends_stats
    history_db = db_client.clan_tags

    ### COLLECTIONS USED ###
    ongoing_stats = legends_stats.ongoing_stats
    server_db = legends_stats.server
    locations = legends_stats.locations
    profile_db = legends_stats.profile_db
    clan_feed_db = legends_stats.clan_feeds
else:
    #### DATABASES USED ####
    legends_stats = db_client.legends_stats
    history_db = db_client.clan_tags

    ### COLLECTIONS USED ###
    ongoing_stats = legends_stats.ongoing_stats
    server_db = legends_stats.server
    locations = legends_stats.locations
    profile_db = legends_stats.profile_db
    '''
    #### DATABASES USED ####
    beta_legends_stats = db_client.beta_legends_stats
    legends_stats = db_client.legends_stats
    history_db = db_client.clan_tags

    ### COLLECTIONS USED ###
    ongoing_stats = beta_legends_stats.beta_ongoing_stats
    server_db = beta_legends_stats.beta_server
    locations = legends_stats.locations
    profile_db = beta_legends_stats.beta_profile_db
    '''

async def patreon_discord_ids():
    ids = []
    headers = {
        "Authorization": f"Bearer {PATREON_BEARER}"}
    url = f"https://www.patreon.com/api/oauth2/api/campaigns/8183553/pledges"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            data = await resp.json(content_type=None)
            inc = data['included']
            for thing in inc:
                if thing["type"] == "user":
                  try:
                    ids.append(int(thing["attributes"]["social_connections"]["discord"]["user_id"]))
                  except:
                    continue

    return ids



async def getTags(ctx, ping):
  ping = str(ping)
  if (ping.startswith('<@') and ping.endswith('>')):
    ping = ping[2:len(ping) - 1]

  if (ping.startswith('!')):
    ping = ping[1:len(ping)]
  id = ping
  tags = await link_client.get_linked_players(id)
  return tags

async def getPlayer(playerTag):
  #print(playerTag)
  try:
    #print("here")
    clashPlayer = await coc_client.get_player(playerTag)
    #print(clashPlayer.name)
    return clashPlayer
  except:
    return None

async def getClan(clanTag):
  try:
    clan = await coc_client.get_clan(clanTag)
    return clan
  except:
    return None

async def verifyPlayer(playerTag, playerToken):
  verified = await coc_client.verify_player_token(playerTag, playerToken)
  return verified


async def getClanWar(clanTag):
  try:
    war = await coc_client.get_clan_war(clanTag)
    return war
  except:
    return None


