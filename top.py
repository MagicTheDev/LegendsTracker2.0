from discord.ext import commands, tasks
import discord
from helper import ongoing_stats, server_db

from discord_slash.utils.manage_components import create_button, wait_for_component, create_select, create_select_option, create_actionrow
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option


class top(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_slash(name="top",
                            description="Top player stats - (hits, def, net).",
                            options=[
                                create_option(
                                    name="stat_type",
                                    description="Filter type",
                                    option_type=3,
                                    required=True,
                                    choices=["Hits", "Defenses", "Net Gain"]
                                ),
                                create_option(
                                    name="scope_type",
                                    description="Scope of stats",
                                    option_type=3,
                                    required=True,
                                    choices=["Server", "All"]
                                )
                            ]
                            )
    async def top_server(self,ctx, stat_type, scope_type):
        if scope_type == "All":
            scope_type = "global"
        else:
            scope_type = "local"
        option_list = ["All", "5000", "5100", "5200", "5300", "5400", "5500", "5600", "5700", "5800", "5900", "6000"]
        select1 = create_select(
            options=[
                create_select_option("All", value=f"All",
                                     description="Based on start of day trophies."),
                create_select_option("5000", value=f"5000",
                                     description="Based on start of day trophies."),
                create_select_option("5100", value=f"5100",
                                     description="Based on start of day trophies."),
                create_select_option("5200", value=f"5200",
                                     description="Based on start of day trophies."),
                create_select_option("5300", value=f"5300",
                                     description="Based on start of day trophies."),
                create_select_option("5400", value=f"5400",
                                     description="Based on start of day trophies."),
                create_select_option("5500", value=f"5500",
                                     description="Based on start of day trophies."),
                create_select_option("5600", value=f"5600",
                                     description="Based on start of day trophies."),
                create_select_option("5700", value=f"5700",
                                     description="Based on start of day trophies."),
                create_select_option("5800", value=f"5800",
                                     description="Based on start of day trophies."),
                create_select_option("5900", value=f"5900",
                                     description="Based on start of day trophies."),
                create_select_option("6000+", value=f"6000",
                                     description="Based on start of day trophies.")
            ],
            placeholder="Choose your option",
            min_values=1,  # the minimum number of options a user must select
            max_values=1  # the maximum number of options a user can select
        )
        selects = create_actionrow(select1)
        selects = [selects]

        embed = await self.createBest(5000, 3000, stat_type, scope_type, ctx)

        msg = await ctx.send(embed=embed, components=selects)

        while True:
            try:
                res = await wait_for_component(self.bot, components=selects,
                                               messages=msg, timeout=600)
            except:
                await msg.edit(components=[])
                break

            if res.author_id != ctx.author.id:
                await res.send(content="You must run the command to interact with components.", hidden=True)
                continue

            await res.edit_origin()
            value = res.values[0]

            if value == "All":
                embed = await self.createBest(5000, 3000, stat_type, scope_type, ctx)
            else:
                embed = await self.createBest(int(value), 100, stat_type, scope_type, ctx)

            await msg.edit(embed=embed,
                           components=selects)

    async def createBest(self, limit, bounds, stat_type, scope, ctx):
        ranking = []


        if scope == "global":
            tracked = ongoing_stats.find()
            lim = await ongoing_stats.count_documents(filter={"league": {"$eq": "Legend League"}})
            playerStats = []
            if limit == 6000:
                bounds = 1000
            for person in await tracked.to_list(length=lim):
                thisPlayer = []
                trophy = person.get("trophies")

                name = person.get("name")
                hits = person.get("today_hits")
                hits = sum(hits)
                defs = person.get("today_defenses")
                numDef = len(defs)
                defs = sum(defs)

                trophy = trophy - (hits - defs)

                if trophy >= limit and trophy < limit + bounds:
                    thisPlayer.append(name)
                    thisPlayer.append(hits)
                    thisPlayer.append(defs)
                    thisPlayer.append(numDef)
                    thisPlayer.append(hits - defs)

                    ranking.append(thisPlayer)
        else:
            results = await server_db.find_one({'server': ctx.guild.id})
            tracked_members = results.get("tracked_members")

            for member in tracked_members:
                person =  await ongoing_stats.find_one({'tag': member})
                league = person.get("league")
                if league != "Legend League":
                    continue

                thisPlayer = []
                trophy = person.get("trophies")

                name = person.get("name")
                hits = person.get("today_hits")
                hits = sum(hits)
                defs = person.get("today_defenses")
                numDef = len(defs)
                defs = sum(defs)

                trophy = trophy - (hits - defs)

                if trophy >= limit and trophy < limit + bounds:
                    thisPlayer.append(name)
                    thisPlayer.append(hits)
                    thisPlayer.append(defs)
                    thisPlayer.append(numDef)
                    thisPlayer.append(hits - defs)

                    ranking.append(thisPlayer)


        eText = ""
        if limit == 5000 and bounds == 3000:
            eText = "5000+"
        elif limit == 6000:
            eText ="6000+"
        else:
            eText = str(limit)

        length = 25
        if length > len(ranking):
            length = len(ranking)

        if stat_type == "Hits":
            ranking = sorted(ranking, key=lambda l: l[1], reverse=True)
            list = ""
            for x in range(0, length):
                name = ranking[x][0]
                hits = ranking[x][1]
                list += f"{str(x + 1)}. {name} | **+{hits}**\n"

            if list == "":
                list = "No players tracked at this trophy level yet."

            embed = discord.Embed(title=f"Leaderboard | Top 25 Hitters | {eText}",
                                  description=list,
                                  color=discord.Color.blue())
            return embed

        elif stat_type == "Defenses":
            ranking = sorted(ranking, key=lambda l: l[2], reverse=False)
            list = ""
            found = 0
            for x in range(0, length):
                name = ranking[x][0]
                defs = ranking[x][2]
                numDef = ranking[x][3]
                if int(numDef) < 8:
                    continue
                else:
                    list += f"{str(found + 1)}. {name} | **-{defs}**\n"
                    found += 1

            if list == "":
                list = "No one tracked has reached 8 defenses yet."

            embed = discord.Embed(title=f"Leaderboard | Top Defenders (8 def) | {eText}",
                                  description=list,
                                  color=discord.Color.blue())
            return embed

        elif stat_type == "Net Gain":
            ranking = sorted(ranking, key=lambda l: l[4], reverse=True)

            list = ""
            for x in range(0, length):
                name = ranking[x][0]
                net = ranking[x][4]
                hits = ranking[x][1]
                defs = ranking[x][2]
                list += f"{str(x + 1)}. {name} | **Net: +{net}** | (+{hits}/-{defs})\n"

            if list == "":
                list = "No one tracked at this trophy level yet."

            embed = discord.Embed(title=f"Leaderboard | Top Net",
                                  description=list,
                                  color=discord.Color.blue())
            return embed









def setup(bot: commands.Bot):
    bot.add_cog(top(bot))