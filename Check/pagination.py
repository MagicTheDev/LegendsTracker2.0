from discord.ext import commands
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component
from discord_slash.model import ButtonStyle


class pagination(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def button_pagination(self, ctx, msg, results):
        # statTypes
        stat_types = ["Yesterday", "Stats", "Graph", "History"]

        check = self.bot.get_cog("CheckStats")
        graph = self.bot.get_cog("graph")

        current_stat = 1
        current_page = 0

        stats_page = []
        for result in results:
            embed = await check.checkEmbed(result, 0)
            stats_page.append(embed)

        await msg.edit(embed=stats_page[0], components=self.create_components(results, current_page),
                       mention_author=False)

        while True:
            try:
                res = await wait_for_component(self.bot, components=self.create_components(results, current_page),
                                               messages=msg, timeout=600)
            except:
                await msg.edit(components=[])
                break

            if res.author_id != ctx.author.id:
                await res.send(content="You must run the command to interact with components.", hidden=True)
                continue

            await res.edit_origin()
            if res.custom_id == "Previous":
                current_page -= 1
                embed = stats_page[current_page]

                await msg.edit(embed=embed,
                               components=self.create_components(results, current_page))

            elif res.custom_id == "Next":

                current_page += 1
                embed = stats_page[current_page]

                await msg.edit(embed=embed,
                               components=self.create_components(results, current_page))

            elif res.custom_id in stat_types:
                current_stat = stat_types.index(res.custom_id)
                embed = await self.display_embed(results, stat_types[current_stat], current_page, ctx)
                await msg.edit(embed=embed,
                               components=self.create_components(results, current_page))

    async def display_embed(self, results, stat_type, current_page, ctx):

        check = self.bot.get_cog("CheckStats")
        graph = self.bot.get_cog("graph")
        history = self.bot.get_cog("History")

        if stat_type == "Stats":
            return await check.checkEmbed(results[current_page], 0)
        elif stat_type == "Yesterday":
            return await check.checkYEmbed(results[current_page])
        elif stat_type == "Graph":
            return await graph.createGraphEmbed(results[current_page])
        elif stat_type == "History":
            return await history.create_history(ctx, results[current_page])

    def create_components(self, results, current_page):
        length = len(results)

        page_buttons = [create_button(label="Prev", emoji="◀️", style=ButtonStyle.blue, disabled=(current_page == 0),
                                      custom_id="Previous"),
                        create_button(label=f"Page {current_page + 1}/{len(results)}", style=ButtonStyle.grey,
                                      disabled=True),
                        create_button(label="Next", emoji="▶️", style=ButtonStyle.blue,
                                      disabled=(current_page == length - 1), custom_id="Next")]
        page_buttons = create_actionrow(*page_buttons)

        stat_buttons = [create_button(label="YStats", style=ButtonStyle.blue, custom_id="Yesterday", disabled=False),
                        create_button(label="Stats", style=ButtonStyle.blue, custom_id="Stats"),
                        create_button(label="Graph", style=ButtonStyle.blue, custom_id="Graph", disabled=False),
                        create_button(label="", emoji="🕑", style=ButtonStyle.blue, custom_id="History")]
        stat_buttons = create_actionrow(*stat_buttons)

        if length == 1:
            return [stat_buttons]

        return [stat_buttons, page_buttons]


def setup(bot: commands.Bot):
    bot.add_cog(pagination(bot))