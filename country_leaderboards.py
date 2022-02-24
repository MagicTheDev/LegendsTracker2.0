
from discord.ext import commands, tasks
from helper import coc_client, locations, ongoing_stats
from discord_slash import cog_ext
from thefuzz import fuzz
from discord_slash.utils.manage_commands import create_option
SUPER_SCRIPTS=["⁰","¹","²","³","⁴","⁵","⁶", "⁷","⁸", "⁹"]
import emoji
import discord
from discord_slash.utils.manage_components import create_button, wait_for_component, create_select, create_select_option, create_actionrow
from discord_slash.model import ButtonStyle

class country_leaderboard(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_slash(name="country_leaderboards",
                       description="Search country leaderboards.",
                       options=[
                           create_option(
                               name="country",
                               description="Search by name or country code.",
                               option_type=3,
                               required=True,
                           ) ]
                       )
    async def country_lb(self, ctx, country):
        await ctx.defer()
        search = country.upper()
        results = await locations.find_one({"country_code" : search})

        msg = None
        embeds = []
        if country.lower() == "global":
            embeds = await self.create_lb("global")
        elif results != None:
            location_id = results.get("location_id")
            embeds = await self.create_lb(location_id)
        else:
            search = country.lower()
            results = locations.find({
                "$text": {
                    "$search": str(self.make_ngrams(search))
                }
            },
            {
                "country_name": True,
                "location_id" : True,
                "score": {
                    "$meta": "textScore"
                }
            }
            ).sort([("score", {"$meta": "textScore"})])

            names = ""
            option_list = []
            for document in await results.to_list(length=5):
                name = document.get("country_name")
                location_id = document.get("location_id")
                match = fuzz.partial_ratio(search, name.lower())
                if name.lower() == country.lower():
                    embeds = await self.create_lb(location_id)
                    break
                if int(match) >=50:
                    names+= f"{name} - {match}% Match\n"
                    option_list.append(create_select_option(f"{name}", value=f"{location_id}"))


            if embeds == []:
                select = create_select(
                    options=option_list,
                    placeholder="Choose a country",  # the placeholder text to show when no options have been chosen
                    min_values=1,  # the minimum number of options a user must select
                    max_values=1,  # the maximum number of options a user can select
                )
                dropdown = [create_actionrow(select)]
                embed = discord.Embed(
                    description=f"**Country Not Found.**\nSimilar Matches Found, Choose from Dropdown List.\n\n{names}",
                    color=discord.Color.blue())

                msg = await ctx.send(embed=embed, components=dropdown)
                value = None
                while value is None:

                    try:
                        res = await wait_for_component(self.bot, components=dropdown,
                                                       messages=msg, timeout=600)
                    except:
                        return await msg.edit(components=[])

                    if res.author_id != ctx.author.id:
                        await res.send(content="You must run the command to interact with components.", hidden=True)
                        continue

                    await res.edit_origin()
                    value = res.selected_options[0]

                location_id = int(value)
                embeds = await self.create_lb(location_id)

        current_page = 0
        if msg is None:
            msg = await ctx.send(embed=embeds[0], components=self.create_components(current_page, embeds))
        else:
            await msg.edit(embed=embeds[0], components=self.create_components(current_page, embeds))

        while True:
            try:
                res = await wait_for_component(self.bot, components=self.create_components(current_page, embeds),
                                               messages=msg, timeout=600)
            except:
                await msg.edit(components=[])
                break

            if res.author_id != ctx.author.id:
                await res.send(content="You must run the command to interact with components.", hidden=True)
                continue

            await res.edit_origin()

            # print(res.custom_id)
            if res.custom_id == "Previous":
                current_page -= 1
                await msg.edit(embed=embeds[current_page],
                               components=self.create_components(current_page, embeds))

            elif res.custom_id == "Next":
                current_page += 1
                await msg.edit(embed=embeds[current_page],
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
                hit_text = f"\n`  ➼` <:sword:825589136026501160> {hits}{numHits} <:clash:877681427129458739> {defs}{numDefs}"

            text += f"`{rank}`\u200e**<:trophyy:849144172698402817>\u200e{member.trophies} | \u200e{name}**{hit_text}\n"
            y += 1
            if y == 20:
                embed = discord.Embed(title=f"**{country_name} Legend Leaderboard**",
                                      description=text)
                y = 0
                embeds.append(embed)
                text = ""

        if text != "":
            embed = discord.Embed(title=f"**{country_name} Legend Leaderboard**",
                                  description=text)
            embeds.append(embed)

        if text == "" and embeds == []:
            text = "No Players"
            embed = discord.Embed(title=f"**{country_name} Legend Leaderboard**",
                                  description=text)
            embeds.append(embed)

        return embeds






    def create_components(self, current_page, embeds):
        length = len(embeds)
        if length == 1:
            return []

        page_buttons = [create_button(label="", emoji="◀️", style=ButtonStyle.blue, disabled=(current_page == 0),
                                      custom_id="Previous"),
                        create_button(label=f"Page {current_page + 1}/{length}", style=ButtonStyle.grey,
                                      disabled=True),
                        create_button(label="", emoji="▶️", style=ButtonStyle.blue,
                                      disabled=(current_page == length - 1), custom_id="Next")
                        ]
        page_buttons = create_actionrow(*page_buttons)

        return [page_buttons]


    def make_ngrams(self, word, min_size=2, prefix_only=False):
        """
        basestring          word: word to split into ngrams
               int      min_size: minimum size of ngrams
              bool   prefix_only: Only return ngrams from start of word
        """
        length = len(word)
        size_range = range(min_size, max(length, min_size) + 1)
        if prefix_only:
            return [
                word[0:size]
                for size in size_range
            ]
        return list(set(
            word[i:i + size]
            for size in size_range
            for i in range(0, max(0, length - size) + 1)
        ))





def setup(bot: commands.Bot):
    bot.add_cog(country_leaderboard(bot))