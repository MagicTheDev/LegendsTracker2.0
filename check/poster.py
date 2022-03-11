import coc
from disnake.ext import commands
import disnake
import matplotlib.pyplot as plt
from utils.helper import ongoing_stats, getPlayer, history_db
from PIL import Image, ImageDraw, ImageFont
import io
from coc import utils
import pytz
utc = pytz.utc
from datetime import datetime
import calendar
from utils.search import search_name_with_tag
import random
import requests
from io import BytesIO

POSTER_LIST = {"Edrag" : "edrag",
               "Hogrider" : "hogrider",
               "Clash Forest" : "clashforest",
               "Clan War" : "clanwar",
               "Loons" : "loons",
               "Witch" : "witch",
               "Archers" : "archers",
               "Bowler" : "bowler",
               "Barbs" : "barbs",
               "Barb & Archer" : "barbandarcher",
               "Big Boy Skelly" : "bigboy",
               "Wiz Tower" : "wiztower",
               "Spells" : "spells",
               "Barb Sunset" : "barbsunset",
               "Wood Board" : "woodboard",
               "Clash Sky" : "clashsky",
               "Super Wizard" : "swiz",
               "Village Battle" : "villagebattle",
               "Hero Pets" : "heropets"}
class Poster(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def autocomp_names(self, user_input: str):
        results = await search_name_with_tag(user_input)
        return results

    @commands.slash_command(name="poster", description="Poster w/ graph & stats to show off season legends stats")
    async def createPoster(self, ctx, smart_search: str = commands.Param(autocomplete=autocomp_names),
                           background: str = commands.Param(default=None,
        choices=["Edrag", "Hogrider", "Clash Forest", "Clan War", "Loons", "Witch", "Archers", "Bowler", "Barbs", "Barb & Archer", "Big Boy Skelly",
                 "Wiz Tower", "Spells", "Barb Sunset", "Wood Board", "Clash Sky", "Super Wizard", "Village Battle", "Hero Pets"]),
                previous_season:str = commands.Param(default=None, choices=["Yes"])):
        """
            Parameters
            ----------
            smart_search: Name or player tag to search with
            background: Which background for poster to use (optional)
            previous_season: (optional)
        """
        await ctx.response.defer()
        if utils.is_valid_tag(smart_search) is False:
            if "|" not in smart_search:
                embed = disnake.Embed(
                    description=f"Invalid player tag or make sure you choose an option from the autocomplete.",
                    color=disnake.Color.red())
                return await ctx.edit_original_message(embed=embed)

        if "|" in smart_search:
            search = smart_search.split("|")
            tag = search[1]
        else:
            tag = smart_search

        tag = utils.correct_tag(tag=tag)
        result = await ongoing_stats.find_one({"tag": tag})
        if result is None:
            embed = disnake.Embed(
                description=f"Player not tracked.\nUse `/track add` to add players for tracking & view stats on them.",
                color=disnake.Color.red())
            return await ctx.edit_original_message(embed=embed)



        if previous_season == "Yes":
            # current season start date
            # use to get previous season (month - 1)
            # end of last season is beginning of current
            end = utils.get_season_start().replace(tzinfo=utc).date()
            start = utils.get_season_start(month=end.month - 1, year=end.year).replace(tzinfo=utc).date()
            month = calendar.month_name[start.month + 1]
            length_of_season = end - start
            length_of_season = length_of_season.days

            # get the first record we need
            # get length progressed in current season
            now = datetime.utcnow().replace(tzinfo=utc).date()
            now_ = datetime.utcnow().replace(tzinfo=utc)
            current_season_progress = now - end
            current_season_progress = current_season_progress.days
            if now_.hour <= 5:
                current_season_progress -= 1

            first_record = current_season_progress
            last_record = first_record + length_of_season
        else:
            start = utils.get_season_start().replace(tzinfo=utc).date()
            now = datetime.utcnow().replace(tzinfo=utc).date()
            now_ = datetime.utcnow().replace(tzinfo=utc)
            current_season_progress = now - start
            current_season_progress = current_season_progress.days
            month = calendar.month_name[start.month + 1]
            if now_.hour <= 5:
                current_season_progress -= 1
            first_record = 0
            last_record = current_season_progress

        name = result.get("name")
        y = result.get("end_of_day")

        len_y = len(y)
        if last_record == len_y:
            last_record -= 1
        if last_record > len_y:
            last_record = len(y) -1

        if first_record >= len_y - 2:
            if previous_season == "Yes":
                embed = disnake.Embed(
                    description=f"Not enough data collected to make a poster for {name}. Minimum 3 days collected last season required.",
                    color=disnake.Color.red())
                return await ctx.edit_original_message(embed=embed)
            else:
                embed = disnake.Embed(
                    description=f"Not enough data collected to make a poster for {name}. {str(len(y))} day collected, minimum 3 required.",
                    color=disnake.Color.red())
                return await ctx.edit_original_message(embed=embed)


        y = y[len(y)-last_record:len(y)-first_record]

        if previous_season != "Yes":
            current = result.get("trophies")
            y.append(current)
        else:
            current = y[-1]

        x = []
        for spot in range(0, len(y)):
            x.append(spot)

        if previous_season != "Yes":
            x.reverse()
        plt.plot(x, y, color='white', linestyle='dashed', linewidth=3,
                      marker="*", markerfacecolor="white", markeredgecolor="yellow", markersize=20)
        plt.ylim(min(y) - 100, max(y) + 100)

        if previous_season != "Yes":
            plt.xlim(int(last_record-first_record + 1), -1)
            plt.xlabel('Days Ago', color="yellow", fontsize=14)
        else:
            plt.xticks([], [])
            plt.xlabel('Trophies Over Time', color="yellow", fontsize=14)

        plt.gca().spines["top"].set_color("yellow")
        plt.gca().spines["bottom"].set_color("yellow")
        plt.gca().spines["left"].set_color("yellow")
        plt.gca().spines["right"].set_color("yellow")
        plt.gca().tick_params(axis='x', colors='yellow')
        plt.gca().tick_params(axis='y', colors='yellow')

        # naming the x axis

        # naming the y axis
        plt.ylabel('Trophies', color="yellow", fontsize=14)
        #encoded_string = name.encode("ascii", "ignore")
        #decode_string = encoded_string.decode()
        plt.savefig("check/poster_graph.png", transparent=True)
        plt.clf()
        plt.close("all")

        graph = Image.open("check/poster_graph.png")
        if background is None:
            poster = Image.open(f"check/{random.choice(list(POSTER_LIST.values()))}.png")
        else:
            poster = Image.open(f"check/{POSTER_LIST.get(background)}.png")

        gspot = None
        flag = None
        cou_spot = None
        if previous_season != "Yes":
            from leaderboards.leaderboard_loop import rankings

            spots = [i for i, value in enumerate(rankings) if value == tag]
            for r in spots:
                loc = rankings[r + 1]
                if loc == "global":
                    gspot = rankings[r + 2]
                else:
                    cou_spot = rankings[r + 2]
                    loc = loc.lower()
                    flag = loc
        else:
            mo = start.month + 1
            if mo <= 9:
                mo = f"0{mo}"
            date = f"{start.year}-{mo}"
            season_stats = history_db[f"{date}"]
            st = await season_stats.find_one({"tag": tag})
            if st is not None:
                r = st.get("rank")
                if r <= 1000:
                    gspot = r

        poster.paste(graph, (1175, 475), graph.convert("RGBA"))

        font = ImageFont.truetype("check/code.TTF", 80)
        font2 = ImageFont.truetype("check/blogger.ttf", 35)
        font3 = ImageFont.truetype("check/blogger.ttf", 60)
        font4 = ImageFont.truetype("check/blogger.ttf",37)
        font5 = ImageFont.truetype("check/blogger.ttf", 20)
        font6 = ImageFont.truetype("check/blogger.ttf", 40)

        #add clan badge & text
        player: coc.Player = await getPlayer(tag)
        if player.clan is not None:
            clan = await player.get_detailed_clan()
            await clan.badge.save("check/clanbadge.png", size="large")
            badge = Image.open("check/clanbadge.png")
            size = 275, 275
            badge.thumbnail(size, Image.ANTIALIAS)
            A = badge.getchannel('A')
            newA = A.point(lambda i: 128 if i > 0 else 0)
            badge.putalpha(newA)
            poster.paste(badge, (1350, 110), badge.convert("RGBA"))

            watermark = Image.new("RGBA", poster.size)
            waterdraw = ImageDraw.ImageDraw(watermark, "RGBA")
            waterdraw.text((1488, 70), clan.name, anchor="mm", font=font)
            watermask = watermark.convert("L").point(lambda x: min(x, 100))
            watermark.putalpha(watermask)
            poster.paste(watermark, None, watermark)

        averages = await self.averages(result, first_record, last_record)
        if averages[2] >= 0:
            avg3 = f"+{str(averages[2])}"
        else:
            avg3 = f"{str(averages[2])}"
        rank = await self.rank(tag, first_record)
        hitstats = await self.hit_stats(result, first_record, last_record)

        draw = ImageDraw.Draw(poster)
        draw.text((585, 95), name, anchor="mm", fill=(255,255,255), font=font)
        draw.text((570, 175), f"Stats collected from {len(y)} days of data", anchor="mm", fill=(255, 255, 255), font=font5)

        draw.text((360, 275), f"+{str(averages[0])} CUPS A DAY", anchor="mm", fill=(255, 255, 255), font=font2)
        draw.text((800, 275), f"-{str(averages[1])} CUPS A DAY", anchor="mm", fill=(255, 255, 255), font=font2)
        draw.text((570, 400), f"{avg3} CUPS A DAY", anchor="mm", fill=(255, 255, 255), font=font2)
        draw.text((1240, 400), f"{current} | Bot Rank #{rank}", fill=(255, 255, 255), font=font3)
        draw.text((295, 670), f"{hitstats[0]}%", anchor="mm", fill=(255, 255, 255), font=font4)
        draw.text((295, 790), f"{hitstats[1]}%", anchor="mm", fill=(255, 255, 255), font=font4)
        draw.text((295, 910), f"{hitstats[2]}%", anchor="mm", fill=(255, 255, 255), font=font4)

        draw.text((840, 670), f"{hitstats[3]}%", anchor="mm", fill=(255, 255, 255), font=font4)
        draw.text((840, 790), f"{hitstats[4]}%", anchor="mm", fill=(255, 255, 255), font=font4)
        draw.text((840, 910), f"{hitstats[5]}%", anchor="mm", fill=(255, 255, 255), font=font4)
        draw.text((75, 1020), f"{month} {start.year} Season", fill=(255, 255, 255), font=font4)

        if gspot is not None:
            globe = Image.open("check/globe.png")
            size = 75,75
            globe.thumbnail(size, Image.ANTIALIAS)
            globe.save("check/globe2.png", "PNG")
            globe = Image.open("check/globe2.png")
            poster.paste(globe, (130, 340), globe.convert("RGBA"))
            draw.text((220, 360), f"#{gspot}", fill=(255, 255, 255), font=font6)


        try:
            if flag is not None:
                globe = Image.open(f"check/png250px/{flag}.png")
                size = 80, 80
                globe.thumbnail(size, Image.ANTIALIAS)
                globe.save(f"check/png250px/{flag}2.png", "PNG")
                globe = Image.open(f"check/png250px/{flag}2.png")
                poster.paste(globe, (770, 350), globe.convert("RGBA"))
                draw.text((870, 355), f"#{cou_spot}", fill=(255, 255, 255), font=font6)
        except:
            pass


        #poster.show()
        temp = io.BytesIO()
        poster.save(temp, format="png")
        temp.seek(0)
        file = disnake.File(fp=temp, filename="filename.png")

        await ctx.edit_original_message(file=file)


    async def averages(self, result, first_record, last_record):
        ongoingOffense = result.get("previous_hits")
        ongoingDefense = result.get("previous_defenses")
        ongoingOffense = ongoingOffense[len(ongoingOffense)-last_record:len(ongoingOffense)-first_record]
        ongoingDefense = ongoingDefense[len(ongoingDefense)-last_record:len(ongoingDefense)-first_record]

        calcOff = []
        x = 0
        for off in ongoingOffense:
            if off != []:
                x += 1
                calcOff.append(sum(off))
        ongoingOffense = calcOff

        calcDef = []
        y = 0
        for defe in ongoingDefense:
            if defe != []:
                y += 1
                calcDef.append(sum(defe))
        ongoingDefense = calcDef

        averageOffense = round(sum(ongoingOffense) / x)
        averageDefense = round(sum(ongoingDefense) / y)
        averageNet = averageOffense - averageDefense

        return[averageOffense, averageDefense, averageNet]


    async def rank(self, ptag, first_record):
        rankings = []
        tracked = ongoing_stats.find()
        limit = await ongoing_stats.count_documents(filter={})
        for document in await tracked.to_list(length=limit):
            tag = document.get("tag")
            if first_record == 0:
                trophy = document.get("trophies")
            else:
                record = first_record + 1
                eod = document.get("end_of_day")
                if record > len(eod):
                    continue
                trophy = eod[-record]

            rr = []
            rr.append(tag)
            rr.append(trophy)
            rankings.append(rr)

        ranking = sorted(rankings, key=lambda l: l[1], reverse=True)
        ranking = await self.get_rank(ptag, ranking)
        return str(ranking+1)

    async def get_rank(self, tag, ranking ):
        for i, x in enumerate(ranking):
            if tag in x:
                return i

    async def hit_stats(self, result, first_record, last_record):
        one_stars = 0
        two_stars = 0
        three_stars = 0

        zero_star_def = 0
        one_stars_def = 0
        two_stars_def = 0
        three_stars_def = 0

        hits = result.get("previous_hits")
        defs = result.get("previous_defenses")
        hits = hits[len(hits)-last_record:len(hits)-first_record]
        defs = defs[len(defs)-last_record:len(defs)-first_record]

        for day in hits:
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

        for day in defs:
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

        return[one_stars_avg, two_stars_avg, three_stars_avg, one_stars_avg_def, two_stars_avg_def, three_stars_avg_def]

def setup(bot: commands.Bot):
    bot.add_cog(Poster(bot))
