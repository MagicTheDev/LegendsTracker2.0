from disnake.ext import commands
import os
import traceback
from utils.helper import IS_BETA

bot = commands.Bot(command_prefix=commands.when_mentioned,
    sync_commands_debug=False, sync_permissions=True, test_guilds=[923764211845312533])


initial_extensions = (
            "check.maincheck",
            "feeds.feeds",
            "leaderboards.leaderboard",
            "stats.mainstats"
            "track.track"            
            "on_events",
            "pepe.pepe",
            "help",
            "settings",
            "patreon"
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