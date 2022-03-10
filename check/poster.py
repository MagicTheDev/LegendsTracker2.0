from disnake.ext import commands
import disnake
import matplotlib.pyplot as plt
from utils.helper import ongoing_stats
from PIL import Image, ImageDraw, ImageFont
import io
from coc import utils

class Poster(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="poster", description="Graph, Stats, & More to show off legends stats.", test_guilds=[923764211845312533, 849364313156485120])
    async def createPoster(self, ctx, player_tag):
        """
            Parameters
            ----------
            player_tag: Player to search for
        """
        await ctx.response.defer()

        if utils.is_valid_tag(player_tag) is True:
            embed = disnake.Embed(
                description=f"Invalid player tag.",
                color=disnake.Color.red())
            await ctx.send(embed)

        tag = utils.correct_tag(tag=player_tag)
        result = await ongoing_stats.find_one({"tag": tag})
        if result is None:
            embed = disnake.Embed(
                description=f"Player not tracked.",
                color=disnake.Color.red())
            await ctx.send(embed)

        y = result.get("end_of_day")
        y = y[-30:]
        current = result.get("trophies")
        y.append(current)
        name = result.get("name")

        if len(y) < 2:
            embed = disnake.Embed(
                description=f"Not enough data collected to make a poster for {name}. {str(len(y))} day collected, minimum 2 required.",
                color=disnake.Color.red())
            await ctx.send(embed)

        x = []
        for spot in range(0, len(y)):
            x.append(spot)

        x.reverse()
        plt.plot(x, y, color='white', linestyle='dashed', linewidth=3,
                      marker="*", markerfacecolor="white", markeredgecolor="yellow", markersize=20)
        plt.ylim(min(y) - 100, max(y) + 100)
        plt.xlim(30, -1)

        plt.gca().spines["top"].set_color("yellow")
        plt.gca().spines["bottom"].set_color("yellow")
        plt.gca().spines["left"].set_color("yellow")
        plt.gca().spines["right"].set_color("yellow")
        plt.gca().tick_params(axis='x', colors='yellow')
        plt.gca().tick_params(axis='y', colors='yellow')

        # naming the x axis
        plt.xlabel('Days Ago', color="yellow", fontsize=14)
        # naming the y axis
        plt.ylabel('Trophies', color="yellow", fontsize=14)
        #encoded_string = name.encode("ascii", "ignore")
        #decode_string = encoded_string.decode()
        plt.savefig("check/poster_graph.png", transparent=True)

        graph = Image.open("check/poster_graph.png")
        poster = Image.open("check/poster.png")

        poster.paste(graph, (1175, 475), graph.convert("RGBA"))

        font = ImageFont.truetype("check/code.TTF", 80)
        font2 = ImageFont.truetype("check/blogger.ttf", 35)
        font3 = ImageFont.truetype("check/blogger.ttf", 60)
        font4 = ImageFont.truetype("check/blogger.ttf",37)
        font5 = ImageFont.truetype("check/blogger.ttf", 20)

        averages = await self.averages(result)
        if averages[2] >= 0:
            avg3 = f"+{str(averages[2])}"
        else:
            avg3 = f"-{str(averages[2])}"
        rank = await self.rank(tag)
        hitstats = await self.hit_stats(result)

        draw = ImageDraw.Draw(poster)
        draw.text((585, 95), name, anchor="mm", fill=(255,255,255), font=font)
        draw.text((570, 175), f"Stats collected from {len(y)} days of data", anchor="mm", fill=(255, 255, 255), font=font5)

        draw.text((360, 275), f"+{str(averages[0])} CUPS A DAY", anchor="mm", fill=(255, 255, 255), font=font2)
        draw.text((800, 275), f"-{str(averages[1])} CUPS A DAY", anchor="mm", fill=(255, 255, 255), font=font2)
        draw.text((570, 400), f"{avg3} CUPS A DAY", anchor="mm", fill=(255, 255, 255), font=font2)
        draw.text((1260, 400), f"{current} | Bot Rank #{rank}", fill=(255, 255, 255), font=font3)
        draw.text((295, 670), f"{hitstats[0]}%", anchor="mm", fill=(255, 255, 255), font=font4)
        draw.text((295, 790), f"{hitstats[1]}%", anchor="mm", fill=(255, 255, 255), font=font4)
        draw.text((295, 910), f"{hitstats[2]}%", anchor="mm", fill=(255, 255, 255), font=font4)

        draw.text((840, 670), f"{hitstats[3]}%", anchor="mm", fill=(255, 255, 255), font=font4)
        draw.text((840, 790), f"{hitstats[4]}%", anchor="mm", fill=(255, 255, 255), font=font4)
        draw.text((840, 910), f"{hitstats[5]}%", anchor="mm", fill=(255, 255, 255), font=font4)


        poster.show()
        temp = io.BytesIO()
        poster.save(temp, format="png")
        temp.seek(0)
        file = disnake.File(fp=temp, filename="filename.png")

        plt.clf()
        plt.close("all")

        await ctx.edit_original_message(file=file)


    async def averages(self, result):
        ongoingOffense = result.get("previous_hits")
        ongoingDefense = result.get("previous_defenses")
        ongoingOffense = ongoingOffense[-30:]
        ongoingDefense = ongoingDefense[-30:]

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


    async def rank(self, ptag):
        rankings = []
        tracked = ongoing_stats.find()
        limit = await ongoing_stats.count_documents(filter={})
        for document in await tracked.to_list(length=limit):
            tag = document.get("tag")
            trophy = document.get("trophies")
            rr = []
            rr.append(tag)
            rr.append(trophy)
            rankings.append(rr)

        ranking = sorted(rankings, key=lambda l: l[1], reverse=True)
        ranking = await self.get_rank(ptag, ranking)
        return str(ranking)

    async def get_rank(self, tag, ranking ):
        for i, x in enumerate(ranking):
            if tag in x:
                return i

    async def hit_stats(self, result):
        one_stars = 0
        two_stars = 0
        three_stars = 0

        zero_star_def = 0
        one_stars_def = 0
        two_stars_def = 0
        three_stars_def = 0

        hits = result.get("previous_hits")
        defs = result.get("previous_defenses")

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