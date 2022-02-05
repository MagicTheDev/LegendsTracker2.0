import asyncio
from discord.ext import commands # Again, we need this imported
import discord
from helper import getClan, getPlayer, verifyPlayer, link_client

from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option


class Linking(commands.Cog):
    """A couple of simple commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_slash(name="history", guild_ids=[328997757048324101, 923764211845312533],
                       description="View a players historical legends data.",
                       options=[
                           create_option(
                               name="player_tag",
                               description="Your account's player tag.",
                               option_type=3,
                               required=True,
                           ),
                           create_option(
                               name="api_token",
                               description="Api_token found in settings.",
                               option_type=3,
                               required=True,
                           )
                       ]
                       )
    async def link(self, ctx, player_tag, api_token):

        try:
          player = await getPlayer(player_tag)
          playerVerified = await verifyPlayer(player.tag, api_token)
          linked = await link_client.get_link(player.tag)

          if (linked is None) and (playerVerified == True):
              link_client.add_link(player.tag, ctx.author.id)
              embed = discord.Embed(
                  title= f"{player.name} has been successfully linked to you.",
                  color=discord.Color.green())
              await ctx.send(embed=embed)

          elif(linked is not None) and (playerVerified == True):
            embed=discord.Embed(title="You're already in the database with that account. Try with a different account or rest easy because I already got you :).", color=discord.Color.green())
            await ctx.send(embed=embed)

          elif (linked is None) and (playerVerified == False):
              embed = discord.Embed(
                  title="The player you are looking for is " + player.name + ", however it appears u may have made a mistake. \nDouble check your api token again...likely a small mistake.",
                  color=discord.Color.red())
              await ctx.send(embed=embed)

          elif(linked is not None) and (playerVerified == False):
            embed = discord.Embed(
                  title=player.name + " is already linked to a discord user.",
                  color=discord.Color.red())
            await ctx.send(embed=embed)

        except:
          embed=discord.Embed(title="Something went wrong :(", description="Take a second glance at your player tag and/or token, one is completely invalid." , color=discord.Color.red())
          await ctx.send(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(Linking(bot))