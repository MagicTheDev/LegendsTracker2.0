from discord.ext import commands, tasks
import discord
from tinydb import TinyDB, Query

import certifi
ca = certifi.where()

import motor.motor_asyncio
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")

from discord_slash.utils.manage_components import create_button, wait_for_component, create_select, create_select_option, create_actionrow
from discord_slash.model import ButtonStyle

ongoing_db = client.legends_stats
ongoing_stats = ongoing_db.ongoing_stats

botDb = TinyDB('botStuff.json')

import asyncio


class best(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='best')
    async def best(self,ctx):
        # print(len(embeds))
        type = 0
        page = 0

        #return await ctx.send("Command under construction.")
        embeds = await self.createBest(5000, 3000)

        msg = await ctx.send(embed=embeds[type][page], components=self.create_components(embeds,page, type, None))


    @commands.Cog.listener()
    async def on_component(self, ctx):
        try:
            type = ctx.component["type"]
            #print(ctx.selected_options)

            if type == 2:
                cid = ctx.component["custom_id"]
                cid = cid.split("_")
                direction = cid[0]
                type = int(cid[1])
                page = int(cid[2])
                try:
                    trophy = int(cid[3])
                except:
                    trophy = cid[3]


                if direction == "Previous":
                    page -=1
                else:
                    page +=1

                if trophy == "None":
                    embeds = await self.createBest(5000, 3000)
                else:
                    embeds = await self.createBest(trophy, 100)

                await ctx.edit_origin(embed=embeds[type][page], components=self.create_components(embeds,page, type, trophy))

            if type == 3:
                cid = ctx.selected_options
                cid = cid[0]
                cid = cid.split("_")
                selected = cid[0]
                type = int(cid[1])
                page = int(cid[2])
                try:
                    trophy = int(cid[3])
                except:
                    trophy = cid[3]

                hit_type = ["Hits", "Defenses", "Net Gain"]

                if selected in hit_type:
                    type = hit_type.index(selected)
                    page = 0
                else:
                    trophy = int(selected)
                    page = 0


                if trophy == "None":
                    embeds = await self.createBest(5000, 3000)
                else:
                    embeds = await self.createBest(trophy, 100)

                await ctx.edit_origin(embed=embeds[type][page],
                                      components=self.create_components(embeds, page, type, trophy))
        except:
            pass


    def create_components(self, embeds, current_page, type, trophy):
        length = len(embeds[type])

        select1 = create_select(
            options=[
                create_select_option("5000", value=f"5000_{type}_{current_page}_{trophy}", description="Based on start of day trophies."),
                create_select_option("5100", value=f"5100_{type}_{current_page}_{trophy}", description="Based on start of day trophies."),
                create_select_option("5200", value=f"5200_{type}_{current_page}_{trophy}", description="Based on start of day trophies."),
                create_select_option("5300", value=f"5300_{type}_{current_page}_{trophy}", description="Based on start of day trophies."),
                create_select_option("5400", value=f"5400_{type}_{current_page}_{trophy}", description="Based on start of day trophies."),
                create_select_option("5500", value=f"5500_{type}_{current_page}_{trophy}", description="Based on start of day trophies."),
                create_select_option("5600", value=f"5600_{type}_{current_page}_{trophy}", description="Based on start of day trophies."),
                create_select_option("5700", value=f"5700_{type}_{current_page}_{trophy}", description="Based on start of day trophies."),
                create_select_option("5800", value=f"5800_{type}_{current_page}_{trophy}", description="Based on start of day trophies."),
                create_select_option("5900", value=f"5900_{type}_{current_page}_{trophy}", description="Based on start of day trophies."),
                create_select_option("6000+", value=f"6000_{type}_{current_page}_{trophy}", description="Based on start of day trophies.")
            ],
            placeholder="Choose your option",
            min_values=1,  # the minimum number of options a user must select
            max_values=1  # the maximum number of options a user can select
        )
        action_row = create_actionrow(select1)

        sword = discord.PartialEmoji(name="sword", id=825589136026501160)
        shield = discord.PartialEmoji(name="clash", id=855491735488036904)

        select2 = create_select(
            options=[
                create_select_option("Hits", value=f"Hits_{type}_{current_page}_{trophy}", emoji=sword),
                create_select_option("Defenses", value=f"Defenses_{type}_{current_page}_{trophy}", emoji=shield),
                create_select_option("Net Gain", value=f"Net Gain_{type}_{current_page}_{trophy}", emoji="➕")
            ],
            placeholder="Choose your option",
            min_values=1,  # the minimum number of options a user must select
            max_values=1  # the maximum number of options a user can select
        )

        action_row2 = create_actionrow(select2)

        buttons = [create_button(style=ButtonStyle.blue, label="◀️ ", custom_id=f"Previous_{type}_{current_page}_{trophy}", disabled=(current_page == 0)),
                   create_button(style=ButtonStyle.grey, label=f"Page {current_page+1}/{length}", disabled=True),
                   create_button(style=ButtonStyle.blue, label="▶️", custom_id=f"Next_{type}_{current_page}_{trophy}", disabled=(current_page == length-1))]
        action_row3 = create_actionrow(*buttons)

        components = [action_row, action_row2, action_row3]

        return components



    async def createBest(self, limit, bounds):

        ranking = []

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
        
        embeds = []
        hitterEmbed = []
        defendEmbed = []
        netEmbed = []

        eText = ""
        if limit == 5000 and bounds == 3000:
            eText = "5000+"
        elif limit == 6000:
            eText ="6000+"
        else:
            eText = str(limit)



        ranking = sorted(ranking, key=lambda l: l[1], reverse=True)
        length = len(ranking)
        list = ""
        for x in range(0, length):
            name = ranking[x][0]
            hits = ranking[x][1]
            #defs = ranking[x][2]
            list += f"{str(x + 1)}. {name} | **+{hits}**\n"
            if x != 0 and (x % 25 == 0 or x == length - 1):
                embed = discord.Embed(title=f"Leaderboard | Top Hitters | {eText}",
                                      description=list,
                                      color=discord.Color.blue())
                hitterEmbed.append(embed)
                list = ""
        
        if hitterEmbed == []:
            embed = discord.Embed(title=f"Leaderboard | Top Hitters | {eText}",
                                  description="No one tracked at this trophy level yet.",
                                  color=discord.Color.blue())
            hitterEmbed.append(embed)

        embeds.append(hitterEmbed)


        ranking = sorted(ranking, key=lambda l: l[2], reverse=False)
        list = ""
        found = 0
        for x in range(0, length):
            name = ranking[x][0]
            #hits = ranking[x][1]
            defs = ranking[x][2]
            numDef = ranking[x][3]
            if int(numDef) < 8:
                continue
            else:
                list += f"{str(found + 1)}. {name} | **-{defs}**\n"
                found += 1

            if found != 0 and (found % 25 == 0 or found == length - 1):
                embed = discord.Embed(title=f"Leaderboard | Top Defenders (8 def) | {eText}",
                                      description=list,
                                      color=discord.Color.blue())
                defendEmbed.append(embed)
                list = ""

        if defendEmbed == []:
            embed = discord.Embed(title=f"Leaderboard | Top Defenders (8  def) | {eText}",
                                  description="No one tracked has reached 8 defenses yet.",
                                  color=discord.Color.blue())
            defendEmbed.append(embed)

        embeds.append(defendEmbed)

        ranking = sorted(ranking, key=lambda l: l[4], reverse=True)
        length = len(ranking)
        list = ""
        for x in range(0, length):
            name = ranking[x][0]
            net = ranking[x][4]
            hits = ranking[x][1]
            defs = ranking[x][2]
            list += f"{str(x + 1)}. {name} | **Net: +{net}** | (+{hits}/-{defs})\n"
            if x != 0 and (x % 25 == 0 or x == length - 1):
                embed = discord.Embed(title=f"Leaderboard | Top Net",
                                      description=list,
                                      color=discord.Color.blue())
                netEmbed.append(embed)
                list = ""
        
        if netEmbed == []:
            embed = discord.Embed(title=f"Leaderboard | Top Net | {eText}",
                                  description="No one tracked at this trophy level yet.",
                                  color=discord.Color.blue())
            netEmbed.append(embed)

        embeds.append(netEmbed)


        return embeds







def setup(bot: commands.Bot):
    bot.add_cog(best(bot))