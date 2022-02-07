from discord.ext import commands
import discord
import matplotlib.pyplot as plt
import io
from helper import ongoing_stats, createTimeStats
import gc

class graph(commands.Cog):

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
            embed = discord.Embed(
                description=f"Not enough data collected to make a graph for {name}. {str(len(y))} day collected, minimum 2 required.",
                color=discord.Color.red())
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
        embed = discord.Embed(title=f"{name}'s Stats Over Time",
                              description=desc,
                              color=discord.Color.blue())
        file = discord.File(fp=buf, filename="filename.png")
        pic_channel = await self.bot.fetch_channel(884951195406458900)
        msg = await pic_channel.send(file=file)
        pic = msg.attachments[0].url
        embed.set_image(url=pic)
        plt.clf()
        plt.close("all")
        gc.collect()
        return embed


def setup(bot: commands.Bot):
    bot.add_cog(graph(bot))