

from disnake.ext import commands
from helper import patreon_discord_ids, server_db



class Patreon(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name='redeem',
                       description="Redeem patreon subscription for this server.")
    async def redeem(self, ctx):
        ids = await patreon_discord_ids()
        if ctx.author.id not in ids:
            return await ctx.send("Sorry, a patreon pledge was not found for this user.")

        results =  await server_db.find_one({"server": ctx.guild.id})
        pat = results.get("patreon_sub")

        if pat is not None:
            if pat == ctx.author.id:
                return await ctx.send("You have already redeemed your pledge on this server.")
            else:
                return await ctx.send("Someone else has already redeemed a pledge on this server.")


        results = await server_db.find_one({"patreon_sub": ctx.author.id})
        if results == None:
            await server_db.update_one({"server": ctx.guild.id}, {'$set': {"patreon_sub": ctx.author.id}})
            return await ctx.send("Pledge successfully linked to this server.")
        else:
            return await ctx.send("Sorry you have already redeemed your pledge on another server. Please join the support server `/server`, to get it switched.")




def setup(bot: commands.Bot):
    bot.add_cog(Patreon(bot))