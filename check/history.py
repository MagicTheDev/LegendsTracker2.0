from disnake.ext import commands
from utils.helper import getPlayer, history_db, coc_client, translate, has_single_plan, has_guild_plan, decrement_usage
import disnake
import calendar


class History(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.slash_command(name="history", description="View a players historical legends data")
    async def history_co(self, ctx: disnake.ApplicationCommandInteraction, player_tag : str):
      """
        Parameters
        ----------
        player_tag: Player to search for
      """
      SINGLE_PLAN = await has_single_plan(ctx)
      GUILD_PLAN = await has_guild_plan(ctx)
      TIER, NUM_COMMANDS, MESSAGE = await decrement_usage(ctx, SINGLE_PLAN, GUILD_PLAN)
      if MESSAGE is not None:
          await ctx.response.defer(ephemeral=True)
          return await ctx.send(content=MESSAGE)

      embed = disnake.Embed(
            description=translate("fetching_history", ctx),
            color=disnake.Color.green())
      await ctx.send(embed=embed)
      embed= await self.create_history(player_tag, ctx)
      await ctx.edit_original_message(embed=embed)

    async def create_history(self, tag, ctx: disnake.ApplicationCommandInteraction):
        dates = await coc_client.get_seasons(league_id=29000022)
        stats = []
        names = []
        player = await getPlayer(tag)
        if player is None:
            embed = disnake.Embed(description=translate("not_valid_player",ctx),
                                  color=disnake.Color.red())
            return embed

        no_results = True
        for date in dates:
            season_stats = history_db[f"{date}"]
            result = await season_stats.find_one({"tag": player.tag})
            if result is not None:
                no_results = False
                stats.append(str(result.get("rank")))
                stats.append(str(result.get("trophies")))
                name = result.get("name")
                if (name != player.name) and (name not in names):
                  names.append(name)
            else:
                stats.append("None")
                stats.append("None")

        if no_results:
          embed = disnake.Embed(description=translate("ended_in_legends", ctx),
                                  color=disnake.Color.red())
          return embed


        text = ""
        oldyear = "2015"
        embed = disnake.Embed(title=f"**{player.name}'s {translate('legend_history',ctx)}**",description=f"🏆= {translate('trophies',ctx)}, 🌎= {translate('global_rank',ctx)}", color=disnake.Color.blue())
        if names != []:
          names = ", ".join(names)
          embed.add_field(name = "**Previous Names**", value=names, inline=False)
        for x in range(0, len(stats),2):
            year = dates[int(x/2)]
            month = year[5:]
            month = calendar.month_name[int(month)]
            month = translate(month, ctx)
            month = month.ljust(9)
            month = f"`{month}`"

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

        if text != "":
            embed.add_field(name = f"**{oldyear}**", value=text, inline=False)

        embed.set_footer(text=translate("tip_history",ctx))
        return embed
        
