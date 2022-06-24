from disnake.ext import commands
from utils.helper import profile_db, ongoing_stats, translate, has_single_plan, has_guild_plan, decrement_usage
import disnake


class QuickCheck(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="quick_check",
                       description="Quickly check the profiles saved to your account (up to 24).",
                       )
    async def saved_profiles(self, ctx: disnake.ApplicationCommandInteraction):
        SINGLE_PLAN = await has_single_plan(ctx)
        GUILD_PLAN = await has_guild_plan(ctx)
        TIER, NUM_COMMANDS, MESSAGE = await decrement_usage(ctx, SINGLE_PLAN, GUILD_PLAN)
        if MESSAGE is not None:
            await ctx.response.defer(ephemeral=True)
            return await ctx.send(content=MESSAGE)

        await ctx.response.defer()
        embed = disnake.Embed(
            description=translate("check_loading", ctx),
            color=disnake.Color.green())
        await ctx.edit_original_message(embed=embed)
        msg = await ctx.original_message()
        results = await profile_db.find_one({'discord_id': ctx.author.id})
        if results is not None:
            tags = results.get("profile_tags")
            for tag in tags:
                r = await ongoing_stats.find_one({"tag": tag})
                if r is None:
                    tags.remove(tag)
                    await profile_db.update_one({'discord_id': ctx.author.id},
                                                {'$pull': {"profile_tags": tag}})
            if tags != []:
                pagination = self.bot.get_cog("MainCheck")
                return await pagination.button_pagination(msg, tags, len(tags) > 1, ctx)

        embed = disnake.Embed(
            description="**No players saved to your profile.**\nTo save a player:\n- Look them up with `/check`\n- Under `Stat Pages & Settings`, click `Quick Check & Daily Report Add/Remove`.\n- Picture Below.",
            color=disnake.Color.red())
        embed.set_image(url="https://cdn.discordapp.com/attachments/843624785560993833/946687559826833428/unknown.png")
        return await msg.edit(content=None, embed=embed)


