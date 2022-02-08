

from discord.ext import commands
import discord

from helper import getPlayer, ongoing_stats


class trophy(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
      

    @commands.Cog.listener()
    async def on_component(self, ctx):
        label = None
        tag= None
        try:
            label = ctx.component["label"]
            tag = ctx.component["custom_id"]
        except:
            pass
        if label == "All Stats":
            await ctx.edit_origin()
            search = self.bot.get_cog("search")
            results = await search.search_results(ctx, tag)

            emojis = self.bot.get_cog("emoji_dictionary")
            legend_shield = emojis.fetch_emojis("legends_shield")
            sword = emojis.fetch_emojis("sword")
            shield = emojis.fetch_emojis("shield")

            for tag in results:
                result = await ongoing_stats.find_one({"tag": tag})
                player = await getPlayer(tag)

                hits = result.get("today_hits")
                defenses = result.get("today_defenses")
                numHits = result.get("num_today_hits")
                numDefs = len(defenses)
                totalOff = sum(hits)
                totalDef = sum(defenses)
                net = totalOff - totalDef
                link = result.get("link")

                clanName = "No Clan"
                if player.clan != None:
                    clanName = player.clan.name

                embed = discord.Embed(title=f"{player.name} ({player.tag}) | {clanName}",
                                      description=f"**Legend's Overview** | [Profile]({link})\n" +
                                                  f"- Started: {legend_shield} {str(player.trophies - net)}, Current: {legend_shield} {str(player.trophies)}\n" +
                                                  f"- {numHits} attacks for +{str(totalOff)} trophies\n" +
                                                  f"- {numDefs} defenses for -{str(totalDef)} trophies\n"
                                                  f"- Net Trophies: {str(net)} trophies\n",
                                      color=discord.Color.blue())

                if player.town_hall == 14:
                    embed.set_thumbnail(
                        url="https://cdn.discordapp.com/attachments/886889518890885141/911184447628513280/1_14_5.png")
                elif player.town_hall == 13:
                    embed.set_thumbnail(
                        url="https://cdn.discordapp.com/attachments/886889518890885141/911184958293430282/786299624725545010.png")

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

                pers = ctx.author
                embed.set_author(name=f"Requested by {pers.display_name}",
                                 icon_url=pers.avatar_url)
                embed.set_footer(text="Message auto-deletes after 120 seconds to reduce clutter.")
                return await ctx.reply(embed=embed, delete_after=120)





def setup(bot: commands.Bot):
    bot.add_cog(trophy(bot))