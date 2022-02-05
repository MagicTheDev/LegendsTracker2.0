import os
import coc
from coc.ext import discordlinks
import motor.motor_asyncio
from dotenv import load_dotenv

load_dotenv()

COC_EMAIL = os.getenv("COC_EMAIL")
COC_PASSWORD = os.getenv("COC_PASSWORD")
DB_LOGIN = os.getenv("DB_LOGIN")
LINK_API_USER = os.getenv("LINK_API_USER")
LINK_API_PW = os.getenv("LINK_API_PW")

coc_client = coc.login(COC_EMAIL, COC_PASSWORD, client=coc.EventsClient, key_count=10, key_names="DiscordBot", throttle_limit = 25)
link_client = discordlinks.login(LINK_API_USER, LINK_API_PW)

db_client = motor.motor_asyncio.AsyncIOMotorClient(DB_LOGIN)

#### DATABASES USED ####
legends_stats = db_client.legends_stats
history_db = db_client.clan_tags

### COLLECTIONS USED ###
ongoing_stats = legends_stats.ongoing_stats
server_db = legends_stats.server
settings_db = legends_stats.settings


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
        "end_of_day": [],
        "clan": clan_name,
        "link": player.share_link,
        "league": str(player.league),
        "highest_streak" : 0,
        "last_updated" : None
      })


async def addLegendsPlayer_SERVER(guild_id, player):
  await server_db.update_one({'server': guild_id},
                                 {'$push': {"tracked_members": player.tag}})

async def removeLegendsPlayer_SERVER(guild_id, player):
  await server_db.update_one({'server': guild_id},
                                 {'$pull': {"tracked_members": player.tag}})


async def createTimeStats(player):
  ongoingOffense = player.get("previous_hits")
  ongoingDefense = player.get("previous_defenses")
  ongoingNet = player.get("ongoingNet")

  calcOff = []
  for off in ongoingOffense:
    calcOff.append(sum(off))
  ongoingOffense = calcOff

  calcDef = []
  for defe in ongoingDefense:
    calcDef.append(sum(defe))
  ongoingDefense = calcDef

  if len(ongoingOffense) == 0:
    text = f"**Average Offense:** No stats collected yet.\n" \
           f"**Average Defense:** No stats collected yet.\n" \
           f"**Average Net Gain:** No stats collected yet.\n"
    return text

  averageOffense = round(sum(ongoingOffense) / len(ongoingOffense))
  averageDefense = round(sum(ongoingDefense) / len(ongoingDefense))
  averageNet = averageOffense - averageDefense

  text = f"**Average Offense:** {averageOffense} cups a day.\n" \
         f"**Average Defense:** {averageDefense} cups a day.\n" \
         f"**Average Net Gain:** {averageNet} cups a day.\n" \
         f"*Stats collected from {len(ongoingOffense)} days of data.*"
  return text


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

async def pingToMember(ctx, ping):
  ping = str(ping)
  if (ping.startswith('<@') and ping.endswith('>')):
    ping = ping[2:len(ping) - 1]

  if (ping.startswith('!')):
    ping = ping[1:len(ping)]

  try:
    member = await ctx.guild.fetch_member(ping)
    return member
  except:
    return None


async def pingToRole(ctx, ping):
    ping = str(ping)
    if (ping.startswith('<@') and ping.endswith('>')):
        ping = ping[2:len(ping) - 1]

    if (ping.startswith('&')):
        ping = ping[1:len(ping)]

    try:
      role = ctx.guild.get_role(int(ping))
      return role
    except:
        return None

async def pingToChannel(ctx, ping):
  ping = str(ping)
  if (ping.startswith('<#') and ping.endswith('>')):
    ping = ping[2:len(ping) - 1]

  try:
    channel =  ctx.guild.get_channel(int(ping))
    return channel
  except:
    return None
