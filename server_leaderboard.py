from discord.ext import commands
from helper import server_db, ongoing_stats
import discord
import emoji
from discord_slash import cog_ext
from PIL import Image, ImageDraw, ImageFont
import io
import random
import math

from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle


class Server_LB(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_slash(name="leaderboard",
                            description="Create a server leaderboard.")
    async def leaderboard(self, ctx):
        await ctx.defer()
        current_page = 0
        file = await self.create_embed(ctx.guild, 0)
        if file is None:
            embed = discord.Embed(description="No players tracked on this server.",
                                  color=discord.Color.blue())
            return await ctx.send(embed=embed)
        page_buttons = [create_button(label="Prev", emoji="◀️", style=ButtonStyle.blue, disabled=(current_page == 0),
                                      custom_id=f"back_{current_page}"),
                        create_button(label=f"",emoji="🔁", style=ButtonStyle.blue, custom_id=f"refresh_{current_page}"),
                        create_button(label="Next", emoji="▶️", style=ButtonStyle.blue,
                                      disabled=(current_page == (file[1]-1)), custom_id=f"forward_{current_page}")]
        page_buttons = create_actionrow(*page_buttons)
        embed = discord.Embed(title=f"{ctx.guild.name} Legends Board",
                              color=discord.Color.blue())

        pic_channel = await self.bot.fetch_channel(884951195406458900)
        msg = await pic_channel.send(file=file[0])
        pic = msg.attachments[0].url
        msg = await ctx.send(pic, components=[page_buttons])


    @commands.Cog.listener()
    async def on_component(self, ctx):

        type = ctx.component["type"]


        if type == 2:
            cid = ctx.component["custom_id"]
            cid = cid.split("_")

            direction = cid[0]
            current_page = int(cid[1])

            if direction == "back":
                current_page -= 1
            elif direction == "forward":
                current_page += 1


            file = await self.create_embed(ctx.guild, current_page)
            page_buttons = [
                create_button(label="Prev", emoji="◀️", style=ButtonStyle.blue, disabled=(current_page == 0),
                              custom_id=f"back_{current_page}"),
                create_button(label=f"", emoji="🔁", style=ButtonStyle.blue, custom_id=f"refresh_{current_page}"),
                create_button(label="Next", emoji="▶️", style=ButtonStyle.blue,
                              disabled=(current_page == (file[1]-1)), custom_id=f"forward_{current_page}")]
            page_buttons = create_actionrow(*page_buttons)
            embed = discord.Embed(title=f"{ctx.guild.name} Legends Board",
                                  color=discord.Color.blue())

            pic_channel = await self.bot.fetch_channel(884951195406458900)
            msg = await pic_channel.send(file=file[0])
            pic = msg.attachments[0].url
            await ctx.send(content=pic, components=[page_buttons], ephemeral=True)


    async def create_embed(self, guild, page):
        results = await server_db.find_one({'server': guild.id})
        tracked_members = results.get("tracked_members")
        if len(tracked_members) == 0:
            return None
        ranking = []

        for member in tracked_members:
            person = await ongoing_stats.find_one({'tag': member})
            league = person.get("league")
            if league != "Legend League":
                continue

            thisPlayer = []
            trophy = person.get("trophies")

            name = person.get("name")
            hits = person.get("today_hits")
            hits = sum(hits)
            numHit = person.get("num_today_hits")
            defs = person.get("today_defenses")
            numDef = len(defs)
            defs = sum(defs)

            started = trophy - (hits - defs)

            thisPlayer.append(name)
            thisPlayer.append(started)
            thisPlayer.append(hits)
            thisPlayer.append(numHit)
            thisPlayer.append(defs)
            thisPlayer.append(numDef)
            thisPlayer.append(trophy)

            ranking.append(thisPlayer)

        ranking = sorted(ranking, key=lambda l: l[6], reverse=True)

        if len(ranking) > 150:
            ranking = ranking[:150]

        max_pages = math.ceil(len(ranking) / 15)

        back = Image.open("legend_board.png")
        mark_image = back.copy()
        font = ImageFont.truetype("thick.ttf", 40)
        font2 = ImageFont.truetype("thick.ttf", 25)
        draw = ImageDraw.Draw(mark_image)

        lower = 15 * page
        upper = lower + 15
        ranking = ranking[lower:upper]


        x = 0
        for player in ranking:

            name = player[0]
            name = emoji.get_emoji_regexp().sub('', name)
            name = name.strip()
            #name = name[:10]
            #name = name.ljust(10)

            started = player[1]
            hits = player[2]
            numHits = player[3]
            defs = player[4]
            numDefs = player[5]
            trophies = player[6]

            width, height = draw.textsize(name, font=font)

            level = random.randint(200, 290)

            if x >= 0 and x <=2:
                draw.text((50, 30 + (165 * x) + height), f"{(x+ 1 +(15 * page))}.", fill=(255, 255, 255), font=font, stroke_width=2,
                          stroke_fill=(0, 0, 0))
                draw.text((370, 35 + (165 * x) + height), f"{level}.", fill=(255, 255, 255), font=font2, stroke_width=2,
                          stroke_fill=(0, 0, 0))
                draw.text((500, 30 + (165*x) + height), name, fill=(255, 255, 255), font=font, stroke_width=2, stroke_fill=(0,0,0))
                draw.text((1000, 30 + (165 * x) + height), f"+{hits}({numHits})", fill=(255, 255, 255), font=font, stroke_width=2,
                          stroke_fill=(0, 0, 0))
                draw.text((1205, 30 + (165 * x) + height), f"/ -{defs}({numDefs})", fill=(255, 255, 255), font=font,
                          stroke_width=2,
                          stroke_fill=(0, 0, 0))
                draw.text((1630, 30 + (165 * x) + height), f"{trophies}", fill=(255, 255, 255), font=font,
                          stroke_width=2,
                          stroke_fill=(0, 0, 0))
            else:
                draw.text((50, 90 + (140 * x) + height), f"{(x+ 1 + (15 * page))}.", fill=(255, 255, 255), font=font, stroke_width=2,
                          stroke_fill=(0, 0, 0))
                draw.text((370, 95 + (140 * x) + height), f"{level}.", fill=(255, 255, 255), font=font2, stroke_width=2,
                          stroke_fill=(0, 0, 0))
                draw.text((500, 90 + (140 * x) + height), name, fill=(255, 255, 255), font=font, stroke_width=2,
                          stroke_fill=(0, 0, 0))
                draw.text((1000, 90 + (140 * x) + height), f"+{hits}({numHits})", fill=(255, 255, 255), font=font, stroke_width=2,
                          stroke_fill=(0, 0, 0))
                draw.text((1205, 90 + (140 * x) + height), f"/ -{defs}({numDefs})", fill=(255, 255, 255), font=font,
                          stroke_width=2,
                          stroke_fill=(0, 0, 0))
                draw.text((1630, 90 + (140 * x) + height), f"{trophies}", fill=(255, 255, 255), font=font,
                          stroke_width=2,
                          stroke_fill=(0, 0, 0))

            x+=1


            if player == ranking[-1]:
                temp = io.BytesIO()
                mark_image.save(temp, format="png")

                temp.seek(0)
                file = discord.File(fp=temp, filename="filename.png")
                return [file, max_pages]















def setup(bot: commands.Bot):
    bot.add_cog(Server_LB(bot))






