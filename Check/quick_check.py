import discord_slash
from discord.ext import commands, tasks
from helper import profile_db
from discord_slash import cog_ext
import discord


class quick_check(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_slash(name="quick_check",
                       description="Quickly check the profiles saved to your account (up to 25).",
                       )
    async def saved_profiles(self, ctx:discord_slash.SlashContext):
        embed = discord.Embed(
            description="<a:loading:884400064313819146> Fetching Stats. | Searches of 10+ players can take a few seconds.",
            color=discord.Color.green())
        msg = await ctx.send(embed=embed)
        results = await profile_db.find_one({'discord_id': ctx.author.id})
        if results != None:
            tags = results.get("profile_tags")
            if tags != []:
                pagination = self.bot.get_cog("pagination")
                return await pagination.button_pagination(ctx, msg, results)

        embed = discord.Embed(
            description="**No players saved to your profile. To save a player, look them up, and under `Stat Pages & Settings`, click `Add to Quick Check`.\nPicture Below.",
            color=discord.Color.red())
        return await msg.edit(content=None, embed=embed)




def setup(bot: commands.Bot):
    bot.add_cog(quick_check(bot))