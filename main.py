import discord
from discord.ext import commands
import os
os.system("pip install \"pymongo[srv]\"")
import traceback
from discord_slash import SlashCommand


bot = commands.Bot(command_prefix=["do ", "Do "], help_command=None)
slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True)




@bot.command(name='reload', hidden=True)
async def _reload(ctx, *, module : str):
    """Reloads a module."""
    if ctx.message.author.id == 706149153431879760:
        try:
            bot.unload_extension(module)
            bot.load_extension(module)
        except:
            await ctx.send('<a:no:862552093324083221> Could not reload module.')
        else:
            await ctx.send('<a:check:861157797134729256> Reloaded module successfully')
    else:
        await ctx.send("You aren't magic. <:PS_Noob:783126177970782228>")

initial_extensions = (
            "Check.check",
            "Check.check_stats",
            "Check.search",
            "Check.graph",
            "Check.pagination",
            "Check.history",
            "on_events",
            "emojis",
            "track",
            "Pepe.pepe",
            "leaderboards",
            "context_menus",
            "top",
            "server_leaderboard",
            "link",
            "stats",
            "help",
            "legend_feed",
            "settings",
            "trophyChanges",
            "country_leaderboards",
            "Check.quick_check"
        )


for extension in initial_extensions:
    try:
        bot.load_extension(extension)
    except Exception as extension:
        traceback.print_exc()




TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)