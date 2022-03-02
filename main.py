import disnake
from disnake.ext import commands
import os
os.system("pip install \"pymongo[srv]\"")
import traceback
from helper import IS_BETA

bot = commands.Bot(command_prefix=commands.when_mentioned,
    sync_commands_debug=True,
    help_command=None)


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
            "top",
            "server_leaderboard",
            "stats",
            "help",
            "legend_feed",
            "settings",
            "trophyChanges",
            "country_leaderboards",
            "Check.quick_check",
            "patreon",
            "ctrack"
        )


def autocomp_names(self, query: str):
    has = []
    for i in initial_extensions:
        if query in i:
            has.append(i)
    return has

@bot.slash_command(name='reload', default_permission=False, guild_ids=[923764211845312533])
@commands.guild_permissions(923764211845312533, owner=True)
@commands.is_owner()
async def _reload(ctx, *, module : str = commands.Param(autocomplete=autocomp_names)):
    """Reloads a module."""
    try:
        bot.unload_extension(module)
        bot.load_extension(module)
    except:
        await ctx.send('<a:no:862552093324083221> Could not reload module.')
    else:
        await ctx.send('<a:check:861157797134729256> Reloaded module successfully')




for extension in initial_extensions:
    try:
        bot.load_extension(extension)
    except Exception as extension:
        traceback.print_exc()



if IS_BETA:
    TOKEN = os.getenv("BETA_TOKEN")
else:
    TOKEN = os.getenv("TOKEN")

bot.run(TOKEN)