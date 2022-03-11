from disnake.ext import commands
import os
import traceback
from utils.helper import IS_BETA

bot = commands.Bot(command_prefix=commands.when_mentioned,
    sync_commands_debug=True, sync_permissions=True)


initial_extensions = (
            "check.maincheck",
            "leaderboards.leaderboard",
            "stats.mainstats",
            "track.track",
            "on_events",
            "pepe.pepe",
            "help",
            "settings",
            "patreon",
            "check.poster",
            "feeds.dm_feed",
            "feeds.feed_buttons",
            "feeds.legend_feed",
            "leaderboards.leaderboard_loop",
            "mainstats"
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
