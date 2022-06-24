from disnake.ext import commands
import disnake
import matplotlib.pyplot as plt
import io
import gc
from dbplayer import DB_Player
from utils.helper import translate


class Graph(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def createGraphEmbed(self, result, ctx):
        player = DB_Player(result)

        y = result.get("end_of_day")
        y = y[-14:]
        current = result.get("trophies")
        y.append(current)
        name = result.get("name")

        if len(y) < 2:
            embed = disnake.Embed(
                description=translate("not_enough_data", ctx).format(name=name, num_day=str(len(y))),
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
            text = f"**{translate('avg_offense',ctx)}:** {translate('no_stats_collected',ctx)}.\n" \
                   f"**{translate('avg_defense',ctx)}:** {translate('no_stats_collected',ctx)}.\n" \
                   f"**{translate('avg_net_gain',ctx)}:** {translate('no_stats_collected',ctx)}.\n"
        else:
            text = f"**{translate('avg_offense',ctx)}:** {player.average_off} {translate('cups_day',ctx)}\n" \
                   f"**{translate('avg_defense',ctx)}:** {player.average_def} {translate('cups_day',ctx)}\n" \
                   f"**{translate('avg_net_gain',ctx)}:** {player.average_net} {translate('cups_day',ctx)}\n" \
                   f"{translate('stats_collected', ctx).format(length=player.length)}"

        embed = disnake.Embed(title=f"{name}'s {translate('season_stats', ctx)}",
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

        embed.add_field(name=f"**{translate('offensive_stats', ctx)}:**",
                        value=f"- {translate('one_star', ctx)}: {player.one_star_avg_off}%\n"
                              f"- {translate('two_star', ctx)}: {player.two_star_avg_off}%\n"
                              f"- {translate('three_star', ctx)}: {player.three_star_avg_off}%\n")

        embed.add_field(name="**Defensive Stats:**",
                        value=f"- {translate('one_star', ctx)}: {player.one_star_avg_def}%\n"
                              f"- {translate('two_star', ctx)}: {player.two_star_avg_def}%\n"
                              f"- {translate('three_star', ctx)}: {player.three_star_avg_def}%\n"
                        )

        return embed
