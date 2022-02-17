from discord.ext import commands
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component, create_select, create_select_option
from helper import ongoing_stats

stat_types = ["Yesterday Legends", "Legends Overview", "Graph & Stats", "Legends History"]

class pagination(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def button_pagination(self, ctx, msg, results):
        check = self.bot.get_cog("CheckStats")

        current_page = 0

        stats_page = []
        trophy_results = []

        x=0
        for result in results:
            r = await ongoing_stats.find_one({"tag": result})
            name = r.get("name")
            trophies = r.get("trophies")
            trophy_results.append(create_select_option(label=f"{name} | 🏆{trophies}", value=f"{x}"))
            embed = await check.checkEmbed(result, 0)
            stats_page.append(embed)
            x+=1

        components = await self.create_components(results, trophy_results)
        await msg.edit(embed=stats_page[0], components=components,
                       mention_author=False)

        while True:
            try:
                res = await wait_for_component(self.bot, components=components,messages=msg, timeout=600)
            except:
                await msg.edit(components=[])
                break


            await res.edit_origin()
            if res.values[0] in stat_types:
                current_stat = stat_types.index(res.values[0])
                embed = await self.display_embed(results, stat_types[current_stat], current_page, ctx)
                components = await self.create_components(results, trophy_results)
                await msg.edit(embed=embed,
                               components=components)
            else:
                try:
                    current_page = int(res.values[0])
                    embed = stats_page[current_page]
                    components = await self.create_components(results, trophy_results)
                    await msg.edit(embed=embed,
                                   components=components)
                except:
                    continue






    async def display_embed(self, results, stat_type, current_page, ctx):

        check = self.bot.get_cog("CheckStats")
        graph = self.bot.get_cog("graph")
        history = self.bot.get_cog("History")

        if stat_type == "Legends Overview":
            return await check.checkEmbed(results[current_page], 0)
        elif stat_type == "Yesterday Legends":
            return await check.checkYEmbed(results[current_page])
        elif stat_type == "Graph & Stats":
            return await graph.createGraphEmbed(results[current_page])
        elif stat_type == "Legends History":
            return await history.create_history(ctx, results[current_page])

    async def create_components(self, results, trophy_results):
        length = len(results)

        options = []

        for stat in stat_types:
            options.append(create_select_option(label=f"{stat}", value=f"{stat}"))

        stat_select  = create_select(
            options=options,
            placeholder="Choose stat page",
            min_values=1,  # the minimum number of options a user must select
            max_values=1  # the maximum number of options a user can select
        )
        stat_select = create_actionrow(stat_select)

        if length == 1:
            return [stat_select]

        profile_select = create_select(
            options=trophy_results,
            placeholder="Choose player",
            min_values=1,  # the minimum number of options a user must select
            max_values=1  # the maximum number of options a user can select
        )
        profile_select = create_actionrow(profile_select)

        return [stat_select, profile_select]


def setup(bot: commands.Bot):
    bot.add_cog(pagination(bot))