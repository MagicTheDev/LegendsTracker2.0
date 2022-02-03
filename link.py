import asyncio
from discord.ext import commands # Again, we need this imported
import discord
from clashClient import getClan, getPlayer, verifyPlayer, client


class Linking(commands.Cog):
    """A couple of simple commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.command(name='link')
    async def link(self, ctx):
        member = ctx.message.author
        executor = ctx.message.author

        playerTag = ""
        playerToken = ""

        messagesSent = []

        embed = discord.Embed(
            title="Hello, " + ctx.author.display_name+ "!",
            description="Let's get started:" +
                        "\nPlease respond with the player tag of __**your**__ account (Example: #PC2UJVVU) You have 5 minutes to reply. See image below for help finding your player tag.", color=0xd4af37)

        embed.set_footer(text="Type `cancel` at any point to quit")
        embed.set_image(
            url="https://media.discordapp.net/attachments/815832030084333628/845542691411853312/image0.jpg")
        msg = await ctx.send(embed=embed)
        messagesSent.append(msg)
        cancel = False
        correctTag = False
        x = 0
        while (correctTag == False):
            x += 1
            if x == 4:
                return
            def check(message):
                ctx.message.content = message.content
                return message.content != "" and message.author == executor

            # LETS SEEE WHAT HAPPENS

            await self.bot.wait_for("message", check=check, timeout=300)
            playerTag = ctx.message.content
            player = await getPlayer(playerTag)
            clan = await getClan(playerTag)

            if (playerTag.lower()== "cancel"):
                cancel = True
                canceled = discord.Embed(
                    description="Command Canceled",
                    color=0xf30000)
                return await ctx.send(embed=canceled)

            if (player == None):
                if clan is not None:
                    embed = discord.Embed(title="Sorry that player tag is invalid and it also appears to be the **clan** tag for " + clan.name,
                                          description="Player tags only, What is the correct player tag?", color=0xf30000)
                    msg = await ctx.send(embed=embed)
                    messagesSent.append(msg)
                else:
                    embed = discord.Embed(title="Sorry that player tag is invalid. Please try again.",
                                          description="What is the correct player tag?", color=0xf30000)
                    msg = await ctx.send(embed=embed)
                    messagesSent.append(msg)
                continue
            else:
                correctTag = True

        #print(str(cancel))

        if cancel is not True:

            embed = discord.Embed(
              title="Next, what is your api token? ",
              description=f"Reference below for help finding your api token. 5 minutes to respond.\nOpen Clash of Clans and navigate to Settings > More Settings or use this link\nhttps://link.clashofclans.com/?action=OpenMoreSettings" +
                          "\nScroll down to the bottom and copy the api token. View the picture below for reference.", color=0xd4af37)
            embed.set_footer(text="Type `cancel` at any point to quit\n(API Token is one-time use.)")
            embed.set_image(url="https://media.discordapp.net/attachments/822599755905368095/826178477023166484/image0.png?width=1806&height=1261")
            msg = await ctx.send(embed=embed)
            messagesSent.append(msg)

            def check(message):
                ctx.message.content = message.content
                return message.content != "" and message.author == executor

            await self.bot.wait_for("message", check=check, timeout=300)
            playerToken = ctx.message.content
            if playerToken.lower() == "cancel":
                cancel = True
                canceled = discord.Embed(
                    description="Command Canceled",
                    color=0xf30000)
                return await ctx.send(embed = canceled)

        if cancel is not True:
            try:
              player = await getPlayer(playerTag)
              playerVerified = await verifyPlayer(player.tag, playerToken)
              linked = await client.get_link(player.tag)

              if (linked is None) and (playerVerified == True):
                  client.add_link(player.tag, member.id)
                  embed = discord.Embed(
                      title="Hey " + member.display_name + f"! {player.name} has been successfully linked to you.",
                      color=discord.Color.green())
                  await ctx.send(embed=embed)


              elif(linked is not None) and (playerVerified == True):
                embed=discord.Embed(title="Hey " + member.display_name + "! You're already in the database with that account ya silly goose. Try with a different account or rest easy because I already got you :).", color=discord.Color.green())
                await ctx.send(embed=embed)

              elif (linked is None) and (playerVerified == False):
                  embed = discord.Embed(
                      title="Hey " + member.display_name + "! The player you are looking for is " + player.name + ", however it appears u may have made a mistake. \nDouble check your player tag and/or api token again...likely a small mistake.",
                      color=discord.Color.red())
                  await ctx.send(embed=embed)

              elif(linked is not None) and (playerVerified == False):
                embed = discord.Embed(
                      title=player.name + " is already linked to a discord user.",
                      color=discord.Color.red())
                await ctx.send(embed=embed)



            except:
              embed=discord.Embed(title="Something went wrong " + member.display_name + " :(", description="Take a second glance at your player tag and/or token, one is completely invalid." , color=discord.Color.red())
              await ctx.send(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(Linking(bot))