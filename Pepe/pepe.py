import asyncio

from discord.ext import commands, tasks
from PIL import Image, ImageDraw, ImageFont
import io
import discord


class pepe(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="pepe")
    async def createPFP(self,ctx, *, sign):
        msg = ctx.message
        try:
            await msg.delete()
        except:
            pass
        channel = ctx.message.channel
        av = ctx.message.author.avatar_url_as(format="png")
        av = await av.read()


        size = 40
        if len(sign) > 20:
            return await ctx.send("Too long, sorry :/")

        if len(sign) >= 11:
            size = 30

        if len(sign) > 14:
            size = 23

        back = Image.open("pepesign.png")

        width = 250
        height = 250
        font = ImageFont.truetype("pepefont.ttf", size)
        draw = ImageDraw.Draw(back)

        draw.text(((width/2)-5, 55), sign, anchor="mm", fill=(0, 0, 0), font=font)

        temp = io.BytesIO()
        back.save(temp, format="png")

        temp.seek(0)
        file = discord.File(fp=temp, filename="filename.png")

        '''
        try:
            webs = await channel.webhooks()
            for web in webs:
                if web.name == ctx.message.author.display_name:
                    await web.send(file=file)
                    return
            web = await channel.create_webhook(name=ctx.message.author.display_name, avatar=av)
            await web.send(file=file)
            #await web.delete()
        except:
        '''

        await ctx.message.author.send(file=file)



def setup(bot: commands.Bot):
    bot.add_cog(pepe(bot))