import discord
from discord.ext import commands
import os
os.system("pip install \"pymongo[srv]\"")
import traceback
from discord_slash import SlashCommand

bot = commands.Bot(command_prefix=[","], help_command=None, intents=discord.Intents().all())
slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True)

embed_color = discord.Color.blue()

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
            "help"
        )


for extension in initial_extensions:
    try:
        bot.load_extension(extension)
    except Exception as extension:
        traceback.print_exc()


TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)