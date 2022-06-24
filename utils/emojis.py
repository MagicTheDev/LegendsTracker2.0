


def fetch_emojis( emojiName):
    switcher = {
        "legends_shield" : "<:legends:881450752109850635>",
        "sword" : "<:sword:825589136026501160>",
        "shield" : "<:clash:877681427129458739>",
        "Previous Days" : "<:cal:989351376146530304>",
        "Legends Overview" : "<:list:989351376796680213>",
        "Graph & Stats" : "<:graph:989351375349624832>",
        "Legends History" : "<:history:989351374087151617>",
        "quick_check" : "<:plusminus:989351373608980490>",
        "gear" : "<:gear:989351372711399504>",
        "pin" : "<:magnify:944914253171810384>",
        "back" : "<:back_arrow:989399022156525650>",
        "forward" : "<:forward_arrow:989399021602877470>",
        "print" : "<:print:989400875766251581>",
        "refresh" : "<:refresh:989399023087652864>",
        "trashcan" : "<:trashcan:989534332425232464>",
        "alphabet" : "<:alphabet:989649421564280872>",
        "start" : "<:start:989649420742176818>",
        "blueshield" : "<:blueshield:989649418665996321>",
        "bluesword" : "<:bluesword:989649419878166558>",
        "bluetrophy" : "<:bluetrophy:989649417760018483>",
        6: "<:06:701579365573459988>",
        7: "<:07:701579365598756874>",
        8: "<:08:701579365321801809>",
        9: "<:09:701579365389041767>",
        10: "<:10:701579365661671464>",
        11: "<:11:701579365699551293>",
        12: "<:12:701579365162418188>",
        13: "<:132:704082689816395787>",
        14: "<:14:828991721181806623>",
    }

    emoji = switcher.get(emojiName, "No Emoji Found")
    return emoji


    

