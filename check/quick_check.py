from disnake.ext import commands
from utils.helper import profile_db
import disnake


class QuickCheck(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="quick_check",
                       description="Quickly check the profiles saved to your account (up to 25).",
                       )
    async def saved_profiles(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.response.defer()
        embed = disnake.Embed(
            description="<a:loading:884400064313819146> Fetching Stats. | Searches of 10+ players can take a few seconds.",
            color=disnake.Color.green())
        await ctx.edit_original_message(embed=embed)
        msg = await ctx.original_message()
        results = await profile_db.find_one({'discord_id': ctx.author.id})
        if results is not None:
            tags = results.get("profile_tags")
            if tags != []:
                pagination = self.bot.get_cog("MainCheck")
                return await pagination.button_pagination(msg, tags, len(tags) > 1)

        embed = disnake.Embed(
            description="**No players saved to your profile.**\nTo save a player:\n- Look them up with `/check`\n- Under `Stat Pages & Settings`, click `Add to Quick Check`.\n- Picture Below.",
            color=disnake.Color.red())
        embed.set_image(url="https://cdn.discordapp.com/attachments/843624785560993833/946687559826833428/unknown.png")
        return await msg.edit(content=None, embed=embed)


