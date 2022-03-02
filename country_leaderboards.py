
from disnake.ext import commands, tasks
from helper import coc_client, locations, ongoing_stats
SUPER_SCRIPTS=["⁰","¹","²","³","⁴","⁵","⁶", "⁷","⁸", "⁹"]
import emoji
import disnake
import re


class country_leaderboard(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    async def autocomp_names(self, query: str):
        query = query.lower()
        query = re.escape(query)
        names = []
        results = locations.find({"country_name": {"$regex": f"^(?i).*{query}.*$"}})
        for document in await results.to_list(length=25):
            names.append(document.get("country_name"))
        return names


    @commands.slash_command(name="country_leaderboards", description="Search country leaderboards.")
    async def country_lb(self, ctx: disnake.ApplicationCommandInteraction , country: str = commands.Param(autocomplete=autocomp_names)):
        await ctx.response.defer()
        loc = await coc_client.get_location_named(country)
        if loc is None:
            return await ctx.edit_original_message(content="Not a valid country. Use the autocomplete to help select from the 100+ countries.")
        embeds = await self.create_lb(loc.id)

        current_page = 0
        await ctx.edit_original_message(embed=embeds[0], components=self.create_components(current_page, embeds))
        msg = await ctx.original_message()
        def check(res: disnake.MessageInteraction):
            return res.message.id == msg.id

        while True:
            try:
                res = await self.bot.wait_for("message_interaction", check=check, timeout=600)
            except:
                await ctx.edit_original_message(components=[])
                break

            if res.author.id != ctx.author.id:
                await res.send(content="You must run the command to interact with components.", ephemeral=True)
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





    async def create_lb(self, location_id):

        if location_id == "global":
            country = await coc_client.get_location_players(location_id="global")
            country_name = "Global"
        else:
            location_id = int(location_id)
            country = await coc_client.get_location_players(location_id=location_id)
            country_name = await coc_client.get_location(location_id)

        x = 1
        text = ""
        embeds = []
        y = 0
        for member in country:
            rank = str(x) + "."
            rank = rank.ljust(3)
            x +=1
            person = await ongoing_stats.find_one({'tag': member.tag})
            name = emoji.get_emoji_regexp().sub('', member.name)
            hit_text = " "
            if person is not None:
                hits = person.get("today_hits")
                hits = sum(hits)
                numHits = person.get("num_today_hits")
                defs = person.get("today_defenses")
                numDefs = len(defs)
                defs = sum(defs)
                if numHits > 9:
                    numHits = 9
                if numDefs > 9:
                    numDefs = 9
                numHits = SUPER_SCRIPTS[numHits]
                numDefs = SUPER_SCRIPTS[numDefs]
                hit_text = f"\n` ➼ ` <:sword:825589136026501160> {hits}{numHits} <:clash:877681427129458739> {defs}{numDefs}"

            text += f"`{rank}`\u200e**<:trophyy:849144172698402817>\u200e{member.trophies} | \u200e{name}**{hit_text}\n"
            y += 1
            if y == 20:
                embed = disnake.Embed(title=f"**{country_name} Legend Leaderboard**",
                                      description=text)
                y = 0
                embeds.append(embed)
                text = ""

        if text != "":
            embed = disnake.Embed(title=f"**{country_name} Legend Leaderboard**",
                                  description=text)
            embeds.append(embed)

        if text == "" and embeds == []:
            text = "No Players"
            embed = disnake.Embed(title=f"**{country_name} Legend Leaderboard**",
                                  description=text)
            embeds.append(embed)

        return embeds



    def create_components(self, current_page, embeds):
        length = len(embeds)
        if length == 1:
            return []

        page_buttons = [disnake.ui.Button(label="", emoji="◀️", style=disnake.ButtonStyle.blurple, disabled=(current_page == 0),
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
    bot.add_cog(country_leaderboard(bot))