from disnake.ext import commands
from utils.helper import patreon_discord_ids, server_db, profile_db
import disnake


class Patreon(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    '''
    @commands.slash_command(name='redeem',
                       description="Redeem a patreon subscription.")
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
        if results is None:
            await server_db.update_one({"server": ctx.guild.id}, {'$set': {"patreon_sub": ctx.author.id}})
            return await ctx.send("Pledge successfully linked to this server.")
        else:
            return await ctx.send("Sorry you have already redeemed your pledge on another server. Please join the support server `/server`, to get it switched.")
    '''
    @commands.slash_command(name="tier_set", description="Owner only command. Sets a tier for a server or user.")
    @commands.is_owner()
    async def set_tier(self, ctx: disnake.ApplicationCommandInteraction, user:disnake.Member=None, guild=None, num_commands:int=0, guild_num_commands: int=0, tier: int= 0, guild_tier:int= 0):
        if user is not None and guild is None:
            results = await profile_db.find_one({'discord_id': user.id})
            if results is None:
                await profile_db.insert_one({'discord_id': user.id,
                                             "num_commands": int(num_commands),
                                             "patreon_tier": int(tier)})
            else:
                await profile_db.update_one({'discord_id': user.id}, {'$set': {"num_commands": int(num_commands),"patreon_tier": int(tier)}})

            await ctx.send(f"{user.mention} set to {num_commands} commands at tier {tier}.")

        elif user is not None and guild is not None:
            results = await profile_db.find_one({'discord_id': user.id})
            if results is None:
                await profile_db.insert_one({'discord_id': user.id,
                                             "num_commands": int(num_commands),
                                             "patreon_tier": int(tier)})
            else:
                await profile_db.update_one({'discord_id': user.id},
                                            {'$set': {"num_commands": int(num_commands), "patreon_tier": int(tier)}})

            guild = guild.split("|")
            guild_id = int(guild[1])
            guild = self.bot.get_guild(guild_id)
            results = await server_db.find_one({"server": guild.id})
            if results is None:
                await server_db.update_one({"server": guild.id}, {'$set': {"patreon_sub": user.id, "num_commands": int(guild_num_commands),
                                             "patreon_tier": int(guild_tier)}})

            await ctx.send(f"{user.mention} given {num_commands} commands at tier {tier}.\n"
                           f"{guild.name} | {guild.id} given {guild_num_commands} @ tier {guild_tier}")

    @set_tier.autocomplete("guild")
    async def auto_guild(self, inter, name):
        guilds = self.bot.guilds
        list = []
        for guild in guilds:
            if name.lower() in guild.name.lower() or name in str(guild.id):
                list.append(f"{guild.name} | {guild.id}")
                if len(list) == 25:
                    return list
        return list



def setup(bot: commands.Bot):
    bot.add_cog(Patreon(bot))
