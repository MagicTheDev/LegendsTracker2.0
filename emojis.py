
from discord.ext import commands

class emoji_dictionary(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def fetch_emojis(self, emojiName):
        switcher = {
            "legends_shield" : "<:legends:881450752109850635>",
            "sword" : "<:sword:825589136026501160>",
            "shield" : "<:clash:877681427129458739>"
        }

        emoji = switcher.get(emojiName, "No Emoji Found")
        return emoji


    

def setup(bot: commands.Bot):
    bot.add_cog(emoji_dictionary(bot))