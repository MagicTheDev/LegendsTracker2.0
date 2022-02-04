from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io
import discord
from discord.commands import slash_command


class pepe(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @slash_command(name="pepe",
                   description="Fun Command. Create a pepe holding a sign w/ text.",
                   guild_ids=[923764211845312533])
    async def createPFP(self,ctx, *, sign_text):

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

        await ctx.respond(content="Save image or copy link & send wherever you like :)",file=file, ephemeral=True)



def setup(bot: commands.Bot):
    bot.add_cog(pepe(bot))