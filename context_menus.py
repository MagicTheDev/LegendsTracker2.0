from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.context import MenuContext
from discord_slash.model import ContextMenuType
import discord


class context_menus(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_context_menu(target=ContextMenuType.USER,
                              name="Check")
    async def context_check(self, ctx: MenuContext):
        await ctx.defer()
        legends = self.bot.get_cog("Check_Slash")
        embed = discord.Embed(
            description="<a:loading:884400064313819146> Fetching Stats.",
            color=discord.Color.green())
        msg = await ctx.reply(embed=embed)
        await legends.legends(ctx, msg, str(ctx.target_author.id))



def setup(bot: commands.Bot):
    bot.add_cog(context_menus(bot))