from discord.ext import commands
import discord

class pagination(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def button_pagination(self, ctx, results):
        #statTypes
        stat_types = ["Yesterday","Stats", "Graph", "History"]

        check = self.bot.get_cog("CheckStats")
        graph = self.bot.get_cog("graph")

        current_stat = 1
        current_page = 0
        
        stats_page = []
        for result in results:
          embed = await check.checkEmbed(result, 0)
          stats_page.append(embed)
        

        await ctx.edit(embed=stats_page[0], view=self.create_components(results,current_page))

        while True:
            try:
                res = await self.bot.wait_for("interaction", timeout=600)
            except:
                await ctx.edit(view=None)
                break


            if res.data["custom_id"] == "Previous":
                current_page -= 1
                embed = stats_page[current_page]

                await ctx.edit(embed=embed,
                               view=self.create_components(results, current_page))

            elif res.data["custom_id"] == "Next":
                current_page += 1
                embed = stats_page[current_page]

                await ctx.edit(embed=embed,
                               view=self.create_components(results, current_page))

            elif res.data["custom_id"] in stat_types:
                current_stat = stat_types.index(res.data["custom_id"])
                embed = await self.display_embed(results, stat_types[current_stat], current_page, ctx)
                await ctx.edit(embed=embed,
                               view=self.create_components(results, current_page))
            


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
            return await history.create_history(ctx,results[current_page])


    def create_components(self, results, current_page):
        length = len(results)

        view = discord.ui.View()
        stat_buttons = [
            discord.ui.Button(label=f"YStats", style=discord.ButtonStyle.primary, custom_id="Yesterday"),
            discord.ui.Button(label=f"Stats", style=discord.ButtonStyle.primary, custom_id="Stats"),
            discord.ui.Button(label=f"Graph", style=discord.ButtonStyle.primary, custom_id="Graph"),
            discord.ui.Button(label=f"", emoji = "🕑", style=discord.ButtonStyle.primary, custom_id="History")
        ]

        for button in stat_buttons:
            view.add_item(button)
        if length == 1:
            return view

        page_buttons = [
            discord.ui.Button(label='Prev', emoji="◀️", style=discord.ButtonStyle.primary, disabled=(current_page == 0),
                              custom_id="Previous", row=2),
            discord.ui.Button(label=f"Page {current_page + 1}/{len(results)}", style=discord.ButtonStyle.grey,
                              disabled=True, row=2),
            discord.ui.Button(label='Next', emoji="▶️", style=discord.ButtonStyle.primary,
                              disabled=(current_page == length - 1), custom_id="Next", row=2)
        ]


        for button in page_buttons:
            view.add_item(button)

        return view



def setup(bot: commands.Bot):
    bot.add_cog(pagination(bot))