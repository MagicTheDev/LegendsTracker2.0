from discord.ext import commands
from helper import getPlayer, history_db
import discord
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option


dates = ["2015-07", "2015-08", "2015-09", "2015-10", "2015-11", "2015-12",
         "2016-01","2016-02","2016-03","2016-04","2016-05","2016-06","2016-07","2016-08","2016-09","2016-10","2016-11","2016-12",
         "2017-01","2017-02","2017-03","2017-04","2017-05","2017-06","2017-07","2017-08","2017-09","2017-10","2017-11","2017-12",
         "2018-01","2018-02","2018-03","2018-04","2018-05","2018-06","2018-07","2018-08","2018-09","2018-10","2018-11","2018-12",
         "2019-01","2019-02","2019-03","2019-04", "2019-05", "2019-06", "2019-07", "2019-08","2019-09","2019-10","2019-11","2019-12",
         "2020-01","2020-02","2020-03","2020-04","2020-05","2020-06","2020-07","2020-08","2020-09","2020-10","2020-11","2020-12",
         "2021-01","2021-02","2021-03","2021-04","2021-05","2021-06","2021-07","2021-08", "2021-09", "2021-10", "2021-11", "2021-12", "2022-01"]

months = ["July", "August", "September", "October", "November", "December","January", "February",
          "March","April","May", "June", "July", "August", "September", "October", "November", "December","January", "February",
          "March","April","May", "June", "July", "August", "September", "October", "November", "December","January", "February",
          "March","April","May", "June", "July", "August", "September", "October", "November", "December","January", "February",
          "March","April","May", "June", "July", "August", "September", "October", "November", "December", "January", "February", "March",
          "April", "May", "June", "July", "August", "September", "October", "November", "December", "January", "February",
          "March","April", "May", "June", "July", "August", "September", "October", "November", "December", "January"]


class History(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_slash(name="history",
                            description="View a players historical legends data.",
                            options=[
                                create_option(
                                    name="player_tag",
                                    description="Player to search for",
                                    option_type=3,
                                    required=True,
                                )]
                            )
    async def history_co(self, ctx, player_tag):
      embed = discord.Embed(
            description="<a:loading:884400064313819146> Fetching Historical Data.",
            color=discord.Color.green())
      msg = await ctx.send(embed=embed)
      embed= await self.create_history(ctx, player_tag)
      await msg.edit(embed=embed)

    async def create_history(self, ctx, tag):
        stats = []
        names = []
        player = await getPlayer(tag)
        if player is None:
            embed = discord.Embed(description="Not a valid player tag. Check the spelling or use a different tag.",
                                  color=discord.Color.red())
            return embed

        no_results = True
        for date in dates:
            season_stats = history_db[f"{date}"]
            result = await season_stats.find_one({"tag": player.tag})
            if result is not None:
                no_results = False
                stats.append(str(result.get("rank")))
                stats.append(str(result.get("trophies")))
                clan = result.get("clan").get("name")
                name = result.get("name")
                rank = str(result.get("rank"))
                trophies = str(result.get("trophies"))
                print(f"Rank: {rank} Trophies: {trophies} Clan: {clan}")
                if (name != player.name) and (name not in names):
                  names.append(name)
            else:
                stats.append("None")
                stats.append("None")

        if no_results == True:
          embed = discord.Embed(description="Player has never ended season in legends.",
                                  color=discord.Color.red())
          return embed


        text = ""
        oldyear = "2015"
        embed = discord.Embed(title=f"**{player.name}'s Legends History**",description="🏆= trophies, 🌎= global rank", color=discord.Color.blue())
        if names != []:
          names = ", ".join(names)
          embed.add_field(name = "**Previous Names**", value=names, inline=False)
        for x in range(0, len(stats),2):
            month = months[int(x/2)]
            month = month.ljust(9)
            month = f"`{month}`"
            year = dates[int(x/2)]
            year = year[0:4]
            rank = stats[x]
            trophies = stats[x+1]
            if rank == "None":
              continue
            if year != oldyear:
              if text != "":
                embed.add_field(name = f"**{oldyear}**", value=text, inline=False)
              oldyear = year
              text = ""
            text += f"{month} | 🏆{trophies} | 🌎{rank}\n"
            
        embed.add_field(name = f"**{oldyear}**", value=text, inline=False)           

        return embed
        

def setup(bot: commands.Bot):
    bot.add_cog(History(bot))