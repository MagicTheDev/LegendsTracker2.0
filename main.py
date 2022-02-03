import discord
from discord.ext import commands
import os
os.system("pip install \"pymongo[srv]\"")

import traceback

bot = commands.Bot(command_prefix=[","], help_command=None, intents=discord.Intents().all())


initial_extensions = (
            "Check.check",
            "Check.search",
            "on_events"
        )

# test comment
@bot.command(name='reload', hidden=True)
async def _reload(ctx, *, module: str):
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

async def createTimeStats(player):
    ongoingOffense = player.get("previous_hits")
    ongoingDefense = player.get("previous_defenses")
    ongoingNet = player.get("ongoingNet")

    calcOff = []
    for off in ongoingOffense:
        calcOff.append(sum(off))
    ongoingOffense = calcOff

    calcDef = []
    for defe in ongoingDefense:
        calcDef.append(sum(defe))
    ongoingDefense = calcDef

    if len(ongoingOffense) == 0:
        text = f"**Average Offense:** No stats collected yet.\n" \
               f"**Average Defense:** No stats collected yet.\n" \
               f"**Average Net Gain:** No stats collected yet.\n"
        return text

    averageOffense = round(sum(ongoingOffense) / len(ongoingOffense))
    averageDefense = round(sum(ongoingDefense) / len(ongoingDefense))
    averageNet = averageOffense - averageDefense

    text = f"**Average Offense:** {averageOffense} cups a day.\n" \
           f"**Average Defense:** {averageDefense} cups a day.\n" \
           f"**Average Net Gain:** {averageNet} cups a day.\n" \
           f"*Stats collected from {len(ongoingOffense)} days of data.*"
    return text




for extension in initial_extensions:
    try:
        bot.load_extension(extension)
    except Exception as extension:
        traceback.print_exc()


TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)