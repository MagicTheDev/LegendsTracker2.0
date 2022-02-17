from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io
import discord
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option


class pepe(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_slash(name="pepe",
                       description="Fun Command. Create a pepe holding a sign w/ text.",
                       options=[
                           create_option(
                               name="sign_text",
                               description="Text to write on sign",
                               option_type=3,
                               required=True,
                           )]
                       )
    async def createPFP(self,ctx, sign_text):

        size = 40
        if len(sign_text) > 20:
            return await ctx.send("Too long, sorry :/")

        if len(sign_text) >= 11:
            size = 30

        if len(sign_text) > 14:
            size = 23

        back = Image.open("Pepe/pepesign.png")

        width = 250
        height = 250
        font = ImageFont.truetype("Pepe/pepefont.ttf", size)
        draw = ImageDraw.Draw(back)

        draw.text(((width/2)-5, 55), sign_text, anchor="mm", fill=(0, 0, 0), font=font)

        temp = io.BytesIO()
        back.save(temp, format="png")

        temp.seek(0)
        file = discord.File(fp=temp, filename="filename.png")

        await ctx.send(content="Save image or copy link & send wherever you like :)",file=file, hidden=True)



def setup(bot: commands.Bot):
    bot.add_cog(pepe(bot))