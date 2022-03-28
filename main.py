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
            "feeds.dm_feed",
            "feeds.feed_buttons",
            "feeds.legend_feed",
            "leaderboards.leaderboard_loop",
            "poster.poster"
        )

"""
Conventions:

server = discord guild object
result(s) = mongo result
type_result(s) - if multiple mongo objects
player = coc.player object
member = coc.player.tag
user = discord.user
user_id = discord.user.id

_id if just the id, not the actual object
"""

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
