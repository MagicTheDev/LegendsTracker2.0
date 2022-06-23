import os
import coc
from coc.ext import discordlinks
import motor.motor_asyncio
from dotenv import load_dotenv
import aiohttp
import json
import disnake
from googletrans import Translator
translator = Translator()
from disnake.ext import commands

IS_BETA = False

load_dotenv()

if not IS_BETA:
    COC_EMAIL = os.getenv("COC_EMAIL")
    COC_PASSWORD = os.getenv("COC_PASSWORD")
    DB_LOGIN = os.getenv("BETA_DB_LOGIN")
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
from pymongo import MongoClient
sync_client = MongoClient(DB_LOGIN)


if not IS_BETA:
    #### DATABASES USED ####
    legends_stats = db_client.legends_stats
    legends_stats2 = sync_client.legends_stats
    history_db = db_client.clan_tags

    ### COLLECTIONS USED ###
    ongoing_stats = legends_stats.ongoing_stats
    server_db = legends_stats.server
    locations = legends_stats.locations
    profile_db2 = legends_stats2.profile_db
    profile_db = legends_stats.profile_db
    clan_feed_db = legends_stats.clan_feeds
else:
    #### DATABASES USED ####
    legends_stats = db_client.legends_stats
    history_db = db_client.clan_tags
    legends_stats2 = sync_client.legends_stats

    ### COLLECTIONS USED ###
    ongoing_stats = legends_stats.ongoing_stats
    server_db = legends_stats.server
    locations = legends_stats.locations
    profile_db2 = legends_stats2.profile_db
    profile_db = legends_stats.profile_db
    clan_feed_db = legends_stats.clan_feeds
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


async def has_single_plan(ctx: disnake.ApplicationCommandInteraction):
    results = await profile_db.find_one({'discord_id': ctx.author.id})
    if results is None:
        return False
    plan = results.get("patreon_sub")
    if plan is None:
        return False
    return True


async def has_guild_plan(ctx: disnake.ApplicationCommandInteraction):
    results =  await server_db.find_one({"server": ctx.guild.id})
    if results is None:
        return False
    plan = results.get("patreon_sub")
    if plan is None:
        return False
    return True

async def decrement_usage(ctx: disnake.ApplicationCommandInteraction, SINGLE_PLAN: bool, GUILD_PLAN: bool, guild_only=False):
    if SINGLE_PLAN and guild_only is False:
        return await single_decrement(ctx)
    else:
        if GUILD_PLAN:
            receipt1 = await guild_decrement(ctx)
            if receipt1[2] is not None and guild_only is not True:
                receipt2 = await free_decrement(ctx)
                if receipt2[2] is not None:
                    return receipt1
                else:
                    return receipt2
            else:
                return receipt1
        else:
            return await free_decrement(ctx)


async def guild_decrement(ctx: disnake.ApplicationCommandInteraction):
    message = None
    results = await server_db.find_one({"server": ctx.guild.id})
    remaining_commands = results.get("num_commands")
    tier = results.get("tier")
    if remaining_commands == 0:
        message = f"**{ctx.author.mention}**, this server has used its monthly command allotment."
        return [tier, remaining_commands, message]
    await server_db.update_one({"server": ctx.guild.id},
                               {'$inc': {'num_commands': -1}})
    remaining_commands -= 1
    return [tier, remaining_commands, message]


async def single_decrement(ctx: disnake.ApplicationCommandInteraction):
    message = None
    results = await profile_db.find_one({'discord_id': ctx.author.id})
    remaining_commands = results.get("num_commands")
    tier = results.get("tier")
    await profile_db.update_one({'discord_id': ctx.author.id},
                                {'$inc': {'num_commands': -1}})
    remaining_commands -= 1
    return [tier, remaining_commands, message]

async def free_decrement(ctx: disnake.ApplicationCommandInteraction):
    message = None

    results = await profile_db.find_one({'discord_id': ctx.author.id})
    if results is None:
        await profile_db.insert_one({'discord_id': ctx.author.id,
                                     "num_commands": 50,
                                     "patreon_tier": 0})
    if results is None:
        results = await profile_db.find_one({'discord_id': ctx.author.id})

    remaining_commands = results.get("num_commands")
    tier = results.get("patreon_tier")

    if remaining_commands == 0:
        message = f"**{ctx.author.mention}**, you have used your 50 free monthly commands.\nVisit <https://www.patreon.com/magicbots> to upgrade to a individual or server plan."
        return [tier, remaining_commands, message]

    if remaining_commands is None:
        await profile_db.update_one({'discord_id': ctx.author.id},
                                    {'$set': {"num_commands": 50,
                                              "patreon_tier": 0}})
        remaining_commands = 50

    await profile_db.update_one({'discord_id': ctx.author.id},
                                {'$inc': {'num_commands': -1}})
    remaining_commands -= 1

    return [tier, remaining_commands, message]



def translate(text, ctx, id=None):
    if ctx is None:
        user_id = id
    else:
        user_id = ctx.author.id

    results = profile_db2.find_one({'discord_id': user_id})
    #results = await profile_db.find_one({'discord_id': user_id})
    if results is None:
        language = "en"
    else:
        language = results.get("language")

    #print(language)
    if language is None:
        language = "en"

    if language != "en":
        translate_file = open(f"text_en.json")
        translate_file = json.load(translate_file)
        text = translate_file[text]
        text = text.replace("\n", "~")
        text = translator.translate(text, dest=language).text
        text = text.replace("~", "\n")
        return text
    else:
        translate_file = open(f"text_{language}.json")
        translate_file = json.load(translate_file)
        return translate_file[text]

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

class MissingGuildPlan(commands.CommandError):
    pass


