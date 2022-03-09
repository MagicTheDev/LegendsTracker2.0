from disnake.ext import commands
import disnake
import matplotlib.pyplot as plt
import io
from utils.helper import ongoing_stats, createTimeStats
import gc

class Graph(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    async def createGraphEmbed(self, results):
        
        result = await ongoing_stats.find_one({"tag": results})
        y = result.get("end_of_day")
        y = y[-14:]
        current = result.get("trophies")
        y.append(current)
        name = result.get("name")


        if len(y) < 2:
            embed = disnake.Embed(
                description=f"Not enough data collected to make a graph for {name}. {str(len(y))} day collected, minimum 2 required.",
                color=disnake.Color.red())
            return embed

        x = []
        for spot in range(0, len(y)):
            x.append(spot)

        x.reverse()

        plt.plot(x, y, color='green', linestyle='dashed', linewidth=3,
                  marker='o', markerfacecolor='blue', markersize=12)
        plt.ylim(min(y) - 100, max(y) + 100)
        plt.xlim(14, -1)

        '''
        for spot in range(-1, 0, 1):
            plt.annotate(y[spot],  # this is the text
                          (x[spot], y[spot]),  # these are the coordinates to position the label
                          textcoords="offset points",  # how to position the text
                          xytext=(5, 10),  # distance from text to points (x,y)
                          ha='right')
        '''
        # naming the x axis
        plt.xlabel('Days Ago')
        # naming the y axis
        plt.ylabel('Trophies')
        encoded_string = name.encode("ascii", "ignore")
        decode_string = encoded_string.decode()
        plt.title(f"{decode_string}'s Trophies Over Time")
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        desc = await createTimeStats(result)
        embed = disnake.Embed(title=f"{name}'s Stats Over Time",
                              description=desc,
                              color=disnake.Color.blue())
        file = disnake.File(fp=buf, filename="filename.png")
        pic_channel = await self.bot.fetch_channel(884951195406458900)
        msg = await pic_channel.send(file=file)
        pic = msg.attachments[0].url
        embed.set_image(url=pic)
        plt.clf()
        plt.close("all")
        gc.collect()


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

        embed.add_field(name="**Offensive Stats:**",
                        value=f"- One Star: {one_stars_avg}%\n"
                              f"- Two Star: {two_stars_avg}%\n"
                              f"- Three Star: {three_stars_avg}%\n"
                              f"- Total {total} attacks accurately tracked.")
        embed.add_field(name="**Defensive Stats:**",
                        value=f"- Zero Star: {zero_stars_avg_def}%\n"
                              f"- One Star: {one_stars_avg_def}%\n"
                              f"- Two Star: {two_stars_avg_def}%\n"
                              f"- Three Star: {three_stars_avg_def}%\n"
                              f"- Total {total_def} defenses accurately tracked."
                        )

        return embed

