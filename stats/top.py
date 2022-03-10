from disnake.ext import commands
import disnake
from utils.helper import ongoing_stats, server_db

class Top(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="top",
                            description="Top player stats - (hits, def, net).")
    async def top_server(self,ctx: disnake.ApplicationCommandInteraction, previous: str = commands.Param(default=None,choices=["Yesterday", "2 Days Ago", "3 Days Ago"])):
        """
            Parameters
            ----------
            previous: (Optional) previous 3 days
        """

        scope_type = "All"
        stat_type = "Hits"
        limit = 5000
        bound = 3000
        if previous == "Yesterday":
            previous = -1
        elif previous == "2 Days Ago":
            previous = -2
        elif previous == "3 Days Ago":
            previous = -3

        option_list = ["All", "5000", "5100", "5200", "5300", "5400", "5500", "5600", "5700", "5800", "5900", "6000"]
        select1 = disnake.ui.Select(
            options=[
                disnake.SelectOption(label="All", value=f"All",
                                     description="Based on start of day trophies."),
                disnake.SelectOption(label="5000", value=f"5000",
                                     description="Based on start of day trophies."),
                disnake.SelectOption(label="5100", value=f"5100",
                                     description="Based on start of day trophies."),
                disnake.SelectOption(label="5200", value=f"5200",
                                     description="Based on start of day trophies."),
                disnake.SelectOption(label="5300", value=f"5300",
                                     description="Based on start of day trophies."),
                disnake.SelectOption(label="5400", value=f"5400",
                                     description="Based on start of day trophies."),
                disnake.SelectOption(label="5500", value=f"5500",
                                     description="Based on start of day trophies."),
                disnake.SelectOption(label="5600", value=f"5600",
                                     description="Based on start of day trophies."),
                disnake.SelectOption(label="5700", value=f"5700",
                                     description="Based on start of day trophies."),
                disnake.SelectOption(label="5800", value=f"5800",
                                     description="Based on start of day trophies."),
                disnake.SelectOption(label="5900", value=f"5900",
                                     description="Based on start of day trophies."),
                disnake.SelectOption(label="6000+", value=f"6000",
                                     description="Based on start of day trophies.")
            ],
            placeholder="Choose trophy range",
            min_values=1,  # the minimum number of options a user must select
            max_values=1  # the maximum number of options a user can select
        )
        st = disnake.ui.ActionRow()
        st.append_item(select1)

        select2 = disnake.ui.Select(
            options=[  # the options in your dropdown
                disnake.SelectOption(label="All", value="All"),
                disnake.SelectOption(label="Server", value="Server"),
            ],
            placeholder="Choose scope type",  # the placeholder text to show when no options have been chosen
            min_values=1,  # the minimum number of options a user must select
            max_values=1,  # the maximum number of options a user can select
        )
        st2 = disnake.ui.ActionRow()
        st2.append_item(select2)

        select3 = disnake.ui.Select(
            options=[  # the options in your dropdown
                disnake.SelectOption(label="Hits", emoji="➕", value="Hits"),
                disnake.SelectOption(label="Defenses", emoji= "➖",value="Defenses"),
                disnake.SelectOption(label="Net Gain", emoji="📈",value="Net Gain")
            ],
            placeholder="Choose stat type",  # the placeholder text to show when no options have been chosen
            min_values=1,  # the minimum number of options a user must select
            max_values=1,  # the maximum number of options a user can select
        )
        st3 = disnake.ui.ActionRow()
        st3.append_item(select3)
        selects = [st, st2, st3]

        scope_options = ["All", "Server"]
        stat_options = ["Hits", "Defenses", "Net Gain"]

        embed = await self.createBest(5000, 3000, stat_type, scope_type, ctx, previous=previous)

        await ctx.send(embed=embed, components=selects)
        msg = await ctx.original_message()

        def check(res: disnake.MessageInteraction):
            return res.message.id == msg.id

        while True:
            try:
                res: disnake.MessageInteraction = await self.bot.wait_for("message_interaction", check=check,
                                                                          timeout=600)
            except:
                await msg.edit(components=[])
                break

            if res.author.id != ctx.author.id:
                await res.send(content="You must run the command to interact with components.", ephemeral=True)
                continue

            value = res.values[0]

            if value in option_list:
                if value == "All":
                    limit = 5000
                    bound = 3000
                    embed = await self.createBest(limit, bound, stat_type, scope_type, ctx, previous=previous)
                else:
                    limit = int(value)
                    bound = 100
                    embed = await self.createBest(limit, bound, stat_type, scope_type, ctx, previous=previous)
            elif value in scope_options:
                scope_type = value
                embed = await self.createBest(limit, bound, stat_type, scope_type, ctx, previous=previous)
            elif value in stat_options:
                stat_type = value
                embed = await self.createBest(limit, bound, stat_type, scope_type, ctx, previous=previous)

            await res.response.edit_message(embed=embed,
                           components=selects)




    async def createBest(self, limit, bounds, stat_type, scope, ctx, previous=None):
        ranking = []

        if scope == "All":
            tracked = ongoing_stats.find()
            lim = await ongoing_stats.count_documents(filter={"league": {"$eq": "Legend League"}})
            playerStats = []
            if limit == 6000:
                bounds = 1000
            for person in await tracked.to_list(length=lim):

                thisPlayer = []
                if previous == None:
                    trophy = person.get("trophies")
                    name = person.get("name")
                    hits = person.get("today_hits")
                    hits = sum(hits)
                    defs = person.get("today_defenses")
                    numDef = len(defs)
                    defs = sum(defs)
                    trophy = trophy - (hits - defs)
                else:
                    trophy = person.get("trophies")
                    name = person.get("name")
                    hits = None
                    defs = None
                    numDef = 8
                    prev_hits = person.get("previous_hits")
                    prev_def = person.get("previous_defenses")

                    needed_length = len(prev_hits)
                    if needed_length < 3:
                        continue
                    for i in range(-1, previous-1, -1):
                        hits = sum(prev_hits[i])
                        defs = sum(prev_def[i])
                        net = hits - defs
                        trophy = trophy - net


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
                if person is None:
                    await server_db.update_one({'server': ctx.guild.id},
                                               {'$pull': {"tracked_members": member}})
                    continue
                league = person.get("league")
                if league != "Legend League":
                    continue

                thisPlayer = []
                if previous == None:
                    trophy = person.get("trophies")
                    name = person.get("name")
                    hits = person.get("today_hits")
                    hits = sum(hits)
                    defs = person.get("today_defenses")
                    numDef = len(defs)
                    defs = sum(defs)
                    trophy = trophy - (hits - defs)
                else:
                    trophy = person.get("trophies")
                    name = person.get("name")
                    hits = None
                    defs = None
                    numDef = 8
                    prev_hits = person.get("previous_hits")
                    prev_def = person.get("previous_defenses")

                    needed_length = len(prev_hits)
                    if needed_length < 3:
                        continue
                    for i in range(-1, previous - 1, -1):
                        hits = sum(prev_hits[i])
                        defs = sum(prev_def[i])
                        net = hits - defs
                        trophy = trophy - net

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

            embed = disnake.Embed(title=f"LB - {scope} | Top 25 Hitters | {eText}",
                                  description=list,
                                  color=disnake.Color.blue())
            return embed

        elif stat_type == "Defenses":
            ranking = sorted(ranking, key=lambda l: l[2], reverse=False)
            list = ""
            found = 0
            for x in ranking:
                name = x[0]
                defs = x[2]
                numDef = x[3]
                if int(numDef) < 8:
                    continue
                print("here")
                list += f"{str(found + 1)}. {name} | **-{defs}**\n"
                found += 1
                if found == 25:
                    break

            if list == "":
                list = "No one tracked has reached 8 defenses yet."

            embed = disnake.Embed(title=f"LB - {scope} | Top Defenders (8 def) | {eText}",
                                  description=list,
                                  color=disnake.Color.blue())
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

            embed = disnake.Embed(title=f"LB - {scope} | Top Net",
                                  description=list,
                                  color=disnake.Color.blue())
            return embed



