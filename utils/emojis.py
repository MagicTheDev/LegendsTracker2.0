


def fetch_emojis( emojiName):
    switcher = {
        "legends_shield" : "<:legends:881450752109850635>",
        "sword" : "<:sword:825589136026501160>",
        "shield" : "<:clash:877681427129458739>"
    }

    emoji = switcher.get(emojiName, "No Emoji Found")
    return emoji


    

