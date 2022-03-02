from disnake.ext import commands
from helper import server_db, ongoing_stats
import disnake
import emoji

SUPER_SCRIPTS=["⁰","¹","²","³","⁴","⁵","⁶", "⁷","⁸", "⁹"]

class Server_LB(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.slash_command(name="leaderboard", description="Server Legends leaderboard (text)")
    async def leaderboard(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.response.defer()
        results = await server_db.find_one({'server': ctx.guild.id})
        tracked_members = results.get("tracked_members")
        if len(tracked_members) == 0:
            return None
        ranking = []

        for member in tracked_members:
            person = await ongoing_stats.find_one({'tag': member})
            if person is None:
                await server_db.update_one({'server': ctx.guild.id},
                                           {'$pull': {"tracked_members": member}})
                continue

            league = person.get("league")
            if league != "Legend League":
                continue

            thisPlayer = []
            trophy = person.get("trophies")

            name = person.get("name")
            name = emoji.get_emoji_regexp().sub('', name)
            name = f"{name}"
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

        text = ""
        initial = f"__**{ctx.guild.name} Legends Leaderboard**__\n"
        embeds = []
        x = 0
        for player in ranking:
            name = player[0]
            hits = player[2]
            hits = player[2]
            numHits = player[3]
            if numHits >= 9:
                numHits = 8
            defs = player[4]
            numDefs = player[5]
            numHits = SUPER_SCRIPTS[numHits]
            numDefs = SUPER_SCRIPTS[numDefs]
            trophies = player[6]
            text += f"\u200e**<:trophyy:849144172698402817>\u200e{trophies} | \u200e{name}**\n➼ <:sword_coc:940713893926428782> {hits}{numHits} <:clash:877681427129458739> {defs}{numDefs}\n"
            x += 1
            if x == 15:
                embed = disnake.Embed(title=f"**{ctx.guild} Legend Leaderboard**",
                                      description=text)
                embed.set_thumbnail(url=ctx.guild.icon.url)
                x = 0
                embeds.append(embed)
                text = ""

        if text != "":
            embed = disnake.Embed(title=f"**{ctx.guild} Legend Leaderboard**",
                                  description=text)
            embed.set_thumbnail(url=ctx.guild.icon.url)
            embeds.append(embed)

        current_page = 0
        await ctx.edit_original_message(embed=embeds[0], components=self.create_components(current_page, embeds))
        msg = await ctx.original_message()

        def check(res: disnake.MessageInteraction):
            return res.message.id == msg.id

        while True:
            try:
                res: disnake.MessageInteraction = await self.bot.wait_for("message_interaction", check=check, timeout=600)
            except:
                await msg.edit(components=[])
                break

            if res.author.id != ctx.author.id:
                await res.send(content="You must run the command yourself to interact with components.", hidden=True)
                continue

            # print(res.custom_id)
            if res.data.custom_id == "Previous":
                current_page -= 1
                await res.response.edit_message(embed=embeds[current_page],
                               components=self.create_components(current_page, embeds))

            elif res.data.custom_id == "Next":
                current_page += 1
                await res.response.edit_message(embed=embeds[current_page],
                               components=self.create_components(current_page, embeds))

    def create_components(self, current_page, embeds):
        length = len(embeds)
        if length == 1:
            return []

        page_buttons = [
            disnake.ui.Button(label="", emoji="◀️", style=disnake.ButtonStyle.blurple, disabled=(current_page == 0),
                              custom_id="Previous"),
            disnake.ui.Button(label=f"Page {current_page + 1}/{length}", style=disnake.ButtonStyle.grey,
                              disabled=True),
            disnake.ui.Button(label="", emoji="▶️", style=disnake.ButtonStyle.blurple,
                              disabled=(current_page == length - 1), custom_id="Next")
            ]
        buttons = disnake.ui.ActionRow()
        for button in page_buttons:
            buttons.append_item(button)

        return [buttons]


def setup(bot: commands.Bot):
    bot.add_cog(Server_LB(bot))






