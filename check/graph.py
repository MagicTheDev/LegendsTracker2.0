from disnake.ext import commands
import disnake
import matplotlib.pyplot as plt
import io
import gc
from dbplayer import DB_Player


class Graph(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def createGraphEmbed(self, result):
        player = DB_Player(result)

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


        # naming the x axis
        plt.xlabel('Days Ago')
        # naming the y axis
        plt.ylabel('Trophies')
        plt.title(f"Trophies - Last 14 Days")
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        if player.length == None or player.length== 0:
            text = f"**Average Offense:** No stats collected yet.\n" \
                   f"**Average Defense:** No stats collected yet.\n" \
                   f"**Average Net Gain:** No stats collected yet.\n"
        else:
            text = f"**Average Offense:** {player.average_off} cups a day.\n" \
                   f"**Average Defense:** {player.average_def} cups a day.\n" \
                   f"**Average Net Gain:** {player.average_net} cups a day.\n" \
                   f"*Stats collected from {player.length} days of data.*"

        embed = disnake.Embed(title=f"{name}'s Season Stats",
                              description=text,
                              color=disnake.Color.blue())
        file = disnake.File(fp=buf, filename="filename.png")
        pic_channel = await self.bot.fetch_channel(884951195406458900)
        msg = await pic_channel.send(file=file)
        pic = msg.attachments[0].url
        embed.set_image(url=pic)
        plt.clf()
        plt.close("all")
        gc.collect()

        embed.add_field(name="**Offensive Stats:**",
                        value=f"- One Star: {player.one_star_avg_off}%\n"
                              f"- Two Star: {player.two_star_avg_off}%\n"
                              f"- Three Star: {player.three_star_avg_def}%\n"
                              f"- Total {player.season_hits_len} attacks accurately tracked.")
        embed.add_field(name="**Defensive Stats:**",
                        value=f"- One Star: {player.one_star_avg_def}%\n"
                              f"- Two Star: {player.two_star_avg_def}%\n"
                              f"- Three Star: {player.three_star_avg_def}%\n"
                              f"- Total {player.season_defs_len} defenses accurately tracked."
                        )

        return embed
