
from disnake.ext import commands
import disnake
from utils.helper import getPlayer, ongoing_stats
from utils.emojis import fetch_emojis
import random

tips = ["New Command! - /poster #playertag"]


class CheckStats(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def checkEmbed(self, results, pre_results=None, player=None):

        legend_shield = fetch_emojis("legends_shield")
        sword = fetch_emojis("sword")
        shield = fetch_emojis("shield")

        from leaderboards.leaderboard_loop import rankings

        if pre_results is None:
            result = await ongoing_stats.find_one({"tag": results})
        else:
            result = pre_results

        if player is None:
            player = await getPlayer(results)

        if player == None:
          embed = disnake.Embed(title=f"{results}",
                                  description=f"Api is likely under maintenance.",
                                  color=disnake.Color.blue())
          return embed
        

        gspot = "<:status_offline:910938138984206347>"
        cou_spot = "<:status_offline:910938138984206347>"
        flag = "🏳️"
        country_name = "- Country: Not Ranked\n"

        spots = [i for i, value in enumerate(rankings) if value == results]


        for r in spots:
            loc = rankings[r + 1]
            if loc == "global" :
                gspot = rankings[r + 2]
            else:
                cou_spot = rankings[r + 2]
                loc = loc.lower()
                flag = f":flag_{loc}:"
                country_name = "- Country: " + rankings[r + 3] + "\n"


        league = result.get("league")
        hits = result.get("today_hits")
        defenses = result.get("today_defenses")
        numHits = result.get("num_today_hits")
        seasonHits = result.get("num_season_hits")
        numDefs = len(defenses)
        totalOff = sum(hits)
        totalDef = sum(defenses)
        net = totalOff - totalDef
        link = result.get("link")

        highest_streak = result.get("highest_streak")
        if highest_streak == None:
            highest_streak = 0
        active_streak = result.get("row_triple")

        if highest_streak != 0:
            highest_streak = f", Highest: {highest_streak}"
        else:
            highest_streak = ""

        active_streak = f"- Triple Streak: {active_streak}{highest_streak}"

        clanName = "No Clan"
        try:
            clanName = player.clan.name
        except:
            pass

        if league != "Legend League":
            embed = disnake.Embed(title=f"{player.name} ({player.tag}) | {clanName}",
                                  description=f"Player not currently in legends.",
                                  color=disnake.Color.blue())
            return embed

        embed = disnake.Embed(
                              description=f"**Legends Overview** | [Profile]({link})\n" +
                                          f"Start: {legend_shield} {str(player.trophies - net)} | Now: {legend_shield} {str(player.trophies)}\n" +
                                          f"- {numHits} attacks for +{str(totalOff)} trophies\n" +
                                          f"- {numDefs} defenses for -{str(totalDef)} trophies\n"
                                          f"- Net Trophies: {str(net)} trophies\n{active_streak}",

                              color=disnake.Color.blue())

        embed.add_field(name= "**Stats**", value=f"- Rank: <a:earth:861321402909327370> {gspot} | {flag} {cou_spot}\n"+ country_name
                                , inline=False)

        if player.town_hall == 14:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/886889518890885141/911184447628513280/1_14_5.png")
        elif player.town_hall == 13:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/886889518890885141/911184958293430282/786299624725545010.png")

        if clanName != "No Clan":
            embed.set_author(name=f"{player.name} ({player.tag}) | {clanName}", icon_url=f"{player.clan.badge.url}")
        else:
            embed.set_author(name=f"{player.name} ({player.tag}) | {clanName}", icon_url="https://cdn.discordapp.com/attachments/880895199696531466/911187298513747998/601618883853680653.png")

        off = ""
        for hit in hits:
            off += f"{sword} +{hit}\n"

        defi = ""
        for d in defenses:
            defi += f"{shield} -{d}\n"

        if off == "":
            off = "No Attacks Yet."
        if defi == "":
            defi = "No Defenses Yet."
        embed.add_field(name="**Offense**", value=off, inline=True)
        embed.add_field(name="**Defense**", value=defi, inline=True)
        embed.set_footer(text=random.choice(tips))

        return embed


    async def checkYEmbed(self, results):

        sword = fetch_emojis("sword")
        shield = fetch_emojis("shield")
        
        result = await ongoing_stats.find_one({"tag": results})
        playerTag = result.get("tag")
        player = await getPlayer(playerTag)
        if player == None:
          embed = disnake.Embed(title=f"{results}",
                                  description=f"Player is invalid, likely banned.",
                                  color=disnake.Color.blue())
          return embed
        league = result.get("league")
        hits = result.get("previous_hits")
        defs = result.get("previous_defenses")
        clanName = "No Clan"
        if player.clan != None:
            clanName = player.clan.name
        try:
            totalOff = sum(hits[-1])
            totalDef = sum(defs[-1])
        except:
            embed = disnake.Embed(title=f"{player.name} ({player.tag}) | {clanName}",
                                  description=f"No stats tracked for yesterday.",
                                  color=disnake.Color.blue())
            return embed

        net = totalOff - totalDef

        if league != "Legend League":
            embed = disnake.Embed(title=f"{player.name} ({player.tag}) | {clanName}",
                                  description=f"Player not currently in legends.",
                                  color=disnake.Color.blue())
            return embed

        embed = disnake.Embed(title=f"{player.name} ({player.tag}) | {clanName}",
                              description="**Legend's Overview Yesterday**\n" +
                                          f"- {str(len(hits[-1]))} attacks for +{str(totalOff)} trophies\n" +
                                          f"- {str(len(defs[-1]))} defenses for -{str(totalDef)} trophies\n"
                                          f"- Net Trophies: {str(net)} trophies",
                              color=disnake.Color.blue())
        off = ""
        for hit in hits[-1]:
            off += f"{sword} +{hit}\n"

        defi = ""
        for d in defs[-1]:
            defi += f"{shield} -{d}\n"

        if off == "":
            off = "No Attacks Tracked."
        if defi == "":
            defi = "No Defenses Tracked."
        embed.add_field(name="**Offense**", value=off, inline=True)
        embed.add_field(name="**Defense**", value=defi, inline=True)
        

        return embed


