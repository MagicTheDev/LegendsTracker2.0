import asyncio
from utils.helper import ongoing_stats, coc_client
import disnake
from disnake.ext import commands
import os

class OwnerCommands(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='reload')
    @commands.is_owner()
    async def _reload(self, ctx, *, module):
        """Reloads a module."""
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except:
            await ctx.send('<a:no:862552093324083221> Could not reload module.')
        else:
            await ctx.send('<a:check:861157797134729256> Reloaded module successfully')

    @commands.command(name='leave')
    @commands.is_owner()
    async def leaveg(self, ctx, *, guild_name):
        guild = disnake.utils.get(self.bot.guilds, name=guild_name)  # Get the guild by name
        if guild is None:
            await ctx.send("No guild with that name found.")  # No guild found
            return
        await guild.leave()  # Guild found
        await ctx.send(f"I left: {guild.name}!")

    @commands.command(name="fix")
    @commands.is_owner()
    async def migrate(self, ctx):

        tracked = ongoing_stats.find()
        limit = await ongoing_stats.count_documents(filter={})
        for document in await tracked.to_list(length=limit):
            hits = document.get("today_hits")
            tag= document.get("tag")
            if sum(hits) >= 321:
                await ongoing_stats.update_one({'tag': tag},
                                               {'$set': {"today_hits": hits[0:7]}})
            else:
                continue

        await ctx.send("done")

    @commands.command(name="gitpull")
    @commands.is_owner()
    async def gitpull(self, ctx):
        os.system("cd LegendsTracker2.0")
        os.system("git pull https://github.com/MagicTheDev/LegendsTracker2.0.git")
        await ctx.send("Bot using latest changes.")

    @commands.command(name="legendfix")
    @commands.is_owner()
    async def test(self, ctx):
        tags = []
        tracked = ongoing_stats.find()
        limit = await ongoing_stats.count_documents(filter={})
        for document in await tracked.to_list(length=limit):
            tag = document.get("tag")
            if tag not in tags:
                tags.append(tag)

        async for player in coc_client.get_players(tags):
            try:
                gspot = player.legend_statistics.previous_season.trophies
                results = await ongoing_stats.find_one({'tag': f"{player.tag}"})
                previous_days = results.get("end_of_day")
                if previous_days == []:
                    continue
                if previous_days[-1] == gspot:
                    continue
                await ongoing_stats.update_one({'tag': f"{player.tag}"},
                                               {'$push': {'end_of_day': gspot}})
                print(gspot)
            except:
                continue

        await ctx.send("Done")


def setup(bot: commands.Bot):
    bot.add_cog(OwnerCommands(bot))