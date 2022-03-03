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
            "ctrack",
            "dm_update"
        )


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