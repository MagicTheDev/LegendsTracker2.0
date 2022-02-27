

from discord.ext import commands
from discord_slash import cog_ext

from helper import patreon_discord_ids, server_db



class Bot_Events(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_slash(name='redeem',
                       description="Redeem patreon subscription for this server.")
    async def redeem(self, ctx):
        ids = await patreon_discord_ids()
        if ctx.user.id not in ids:
            return await ctx.send("Sorry, a patreon pledge was not found for this user.")

        results =  await server_db.find_one({"server": ctx.guild.id})
        pat = results.get("patreon_sub")

        if pat is not None:
            if pat == ctx.user.id:
                return await ctx.send("You have already redeemed your pledge on this server.")
            else:
                return await ctx.send("Someone else has already redeemed a pledge on this server.")


        results = await server_db.find_one({"patreon_sub": ctx.user.id})
        if results == None:
            await server_db.update_one({"server": ctx.guild.id}, {'$set': {"patreon_sub": ctx.user.id}})
            return await ctx.send("Pledge successfully linked to this server.")
        else:
            return await ctx.send("Sorry you have already redeemed your pledge on another server. Please join the support server `/server`, to get it switched.")




def setup(bot: commands.Bot):
    bot.add_cog(Bot_Events(bot))