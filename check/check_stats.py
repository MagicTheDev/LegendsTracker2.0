
from disnake.ext import commands
import disnake
from utils.helper import translate
from utils.emojis import fetch_emojis
from coc import utils
import pytz
utc = pytz.utc
from datetime import datetime
import calendar
from dbplayer import DB_Player

SUPER_SCRIPTS=["⁰","¹","²","³","⁴","⁵","⁶", "⁷","⁸", "⁹"]

class CheckStats(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def checkEmbed(self, result, ctx):
        player = DB_Player(result)

        legend_shield = fetch_emojis("legends_shield")
        sword = fetch_emojis("sword")
        shield = fetch_emojis("shield")

        from leaderboards.leaderboard_loop import rankings

        gspot = "<:status_offline:910938138984206347>"
        cou_spot = "<:status_offline:910938138984206347>"

        if player.location is None:
            country_name = translate("unranked_country", ctx)
            flag = "🏳️"
        else:
            country_name = f"- " + translate("country",ctx)+ f" {player.location}\n"
            flag = f":flag_{player.location_code.lower()}:"

        spots = [i for i, value in enumerate(rankings) if value == player.tag]

        for r in spots:
            loc = rankings[r + 1]
            if loc == "global" :
                gspot = rankings[r + 2]
            else:
                cou_spot = rankings[r + 2]
                loc = loc.lower()
                flag = f":flag_{loc}:"
                tr_country = translate("country", ctx)
                country_name = f"- {tr_country}: " + rankings[r + 3] + "\n"


        if player.highest_streak != 0:
            tr_highest = translate("highest", ctx)
            highest_streak = f", {tr_highest}: {player.highest_streak}"
        else:
            highest_streak = ""

        tr_streak = translate("triple_streak", ctx)
        active_streak = f"- {tr_streak}: {player.current_streak}{highest_streak}"

        if player.league != "Legend League":
            embed = disnake.Embed(title=f"{player.name} ({player.tag}) | {player.clan_name}",
                                  description=translate("not_in_legends", ctx),
                                  color=disnake.Color.blue())
            return embed

        tr_overview = translate("legend_overview", ctx)
        tr_profile = translate("profile", ctx)
        diff = str(player.trophies - player.todays_net)
        embed = disnake.Embed(
                              description=f"**{tr_overview}** | [{tr_profile}]({player.link})\n" +
                                          translate("start_now", ctx).format(legend_shield=legend_shield, diff=diff, player_trophies=player.trophies) +
                                          translate("check_attacks", ctx).format(player_num_hits=player.num_hits, player_sum_hits=player.sum_hits) +
                                          translate("check_defenses", ctx).format(player_num_def=player.num_def,player_sum_defs=player.sum_defs) +
                                          translate("net_trophies",ctx).format(player_todays_net=player.todays_net, active_streak=active_streak),
                              color=disnake.Color.blue())

        embed.add_field(name= f"**{translate('stats', ctx)}**", value=f"- {translate('rank', ctx)}: <a:earth:861321402909327370> {gspot} | {flag} {cou_spot}\n"+ country_name
                                , inline=False)

        if player.town_hall == 14:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/886889518890885141/911184447628513280/1_14_5.png")
        elif player.town_hall == 13:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/886889518890885141/911184958293430282/786299624725545010.png")

        if player.clan_name != "No Clan":
            embed.set_author(name=f"{player.name} | {player.clan_name}", icon_url=f"{player.clan_badge_link}", url=player.link)
        else:
            embed.set_author(name=f"{player.name} | {player.clan_name}", icon_url="https://cdn.discordapp.com/attachments/880895199696531466/911187298513747998/601618883853680653.png")

        off = ""
        for hit in player.todays_hits:
            off += f"{sword} +{hit}\n"

        defi = ""
        for d in player.today_defs:
            defi += f"{shield} -{d}\n"

        if off == "":
            off = translate("no_attacks_yet", ctx)
        if defi == "":
            defi = translate("no_defenses_yet", ctx)
        embed.add_field(name=f"**{translate('offense',ctx)}**", value=off, inline=True)
        embed.add_field(name=f"**{translate('defense',ctx)}**", value=defi, inline=True)
        embed.set_footer(text=player.tag)

        return embed


    async def checkYEmbed(self, result, ctx):
        player = DB_Player(result)

        sword = fetch_emojis("sword")
        shield = fetch_emojis("shield")

        if len(player.previous_hits) == 0:
            embed = disnake.Embed(title=f"{player.name} ({player.tag}) | {player.clan_name}",
                                  description=translate("no_previous_stats", ctx),
                                  color=disnake.Color.blue())
            return embed

        if player.league != "Legend League":
            embed = disnake.Embed(title=f"{player.name} ({player.tag}) | {player.clan_name}",
                                  description=translate("not_in_legends", ctx),
                                  color=disnake.Color.blue())
            return embed

        start = utils.get_season_start().replace(tzinfo=utc).date()
        now = datetime.utcnow().replace(tzinfo=utc).date()
        now_ = datetime.utcnow().replace(tzinfo=utc)
        current_season_progress = now - start
        current_season_progress = current_season_progress.days

        if now_.hour < 5:
            current_season_progress -= 1
        first_record = 0
        last_record = current_season_progress
        real = last_record
        eod = result.get("end_of_day")

        len_y = len(eod)
        if last_record > len_y:
            last_record = len(eod)

        text = f""
        initial = f"**{translate('attacks_won',ctx)}:** {player.num_season_hits} | **{translate('defenses_won',ctx)}:** {player.num_season_defs}\n"
        text += initial
        day = (((last_record - real) * -1))
        hits = player.previous_hits[len(player.previous_hits) - last_record:len(player.previous_hits) - first_record]
        defs = player.previous_defs[len(player.previous_defs) - last_record:len(player.previous_defs) - first_record]

        spot = 0
        for hit in hits:
            day+=1
            numHits = len(hit)
            if numHits >= 9:
                numHits = 8
            def_spot = defs[spot]
            numDefs = len(def_spot)
            if numDefs >= 9:
                numHits = 8
            numHits = SUPER_SCRIPTS[numHits]
            numDefs = SUPER_SCRIPTS[numDefs]
            spot+=1

            day_text = f"{translate('day',ctx)} {day}"
            day_text = day_text.ljust(6)
            text+=f"`{day_text}` <:sword:948471267604971530>{sum(hit)}{numHits} <:clash:877681427129458739> {sum(def_spot)}{numDefs}\n"

        if text == initial:
            text += f"\n**{translate('no_previous_days',ctx)}**"
        embed = disnake.Embed(title=translate("season_legends_overview",ctx),
                              description=text,
                              color=disnake.Color.blue())

        if player.clan_name != "No Clan" and player.clan_badge_link != "No Clan":
            embed.set_author(name=f"{player.name} | {player.clan_name}", icon_url=f"{player.clan_badge_link}", url=player.link)
            if player.town_hall == 14:
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/886889518890885141/911184447628513280/1_14_5.png")
            elif player.town_hall == 13:
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/886889518890885141/911184958293430282/786299624725545010.png")
        else:
            embed.set_author(name=f"{player.name} | {player.clan_name}", icon_url="https://cdn.discordapp.com/attachments/880895199696531466/911187298513747998/601618883853680653.png")

        month = calendar.month_name[start.month + 1]
        embed.set_footer(text=f"{month} {start.year} {translate('season',ctx)}")

        return embed



