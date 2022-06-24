import disnake
from utils.discord import partial_emoji_gen
from utils.emojis import fetch_emojis
from utils.helper import translate

def create_components(bot, current_page, embeds, print=False):
    length = len(embeds)
    if length == 1:
        return []

    if not print:
        page_buttons = [
            disnake.ui.Button(label="", emoji=partial_emoji_gen(bot, fetch_emojis("back")), style=disnake.ButtonStyle.grey, disabled=(current_page == 0),
                              custom_id="Previous"),
            disnake.ui.Button(label=f"Page {current_page + 1}/{length}", style=disnake.ButtonStyle.grey,
                              disabled=True),
            disnake.ui.Button(label="", emoji=partial_emoji_gen(bot, fetch_emojis("forward")), style=disnake.ButtonStyle.grey,
                              disabled=(current_page == length - 1), custom_id="Next")
            ]
    else:
        page_buttons = [
            disnake.ui.Button(label="", emoji=partial_emoji_gen(bot, fetch_emojis("back")), style=disnake.ButtonStyle.grey, disabled=(current_page == 0),
                              custom_id="Previous"),
            disnake.ui.Button(label=f"Page {current_page + 1}/{length}", style=disnake.ButtonStyle.grey,
                              disabled=True),
            disnake.ui.Button(label="", emoji=partial_emoji_gen(bot, fetch_emojis("forward")), style=disnake.ButtonStyle.grey,
                              disabled=(current_page == length - 1), custom_id="Next"),
            disnake.ui.Button(label="", emoji=partial_emoji_gen(bot, fetch_emojis("print")), style=disnake.ButtonStyle.grey,
                              custom_id="Print")
        ]

    buttons = disnake.ui.ActionRow()
    for button in page_buttons:
        buttons.append_item(button)

    return [buttons]


def leaderboard_components(bot, current_page, embeds, ctx):
    length = len(embeds)

    select = disnake.ui.Select(
        options=[  # the options in your dropdown
            disnake.SelectOption(label=translate("alphabetic", ctx), emoji=partial_emoji_gen(bot, fetch_emojis("alphabet")), value="0"),
            disnake.SelectOption(label=translate("started", ctx), emoji=partial_emoji_gen(bot, fetch_emojis("start")), value="1"),
            disnake.SelectOption(label=translate("offense", ctx), emoji=partial_emoji_gen(bot, fetch_emojis("bluesword")), value="2"),
            disnake.SelectOption(label=translate("defense", ctx), emoji=partial_emoji_gen(bot, fetch_emojis("blueshield")), value="4"),
            disnake.SelectOption(label=translate("trophies_upc", ctx), emoji=partial_emoji_gen(bot, fetch_emojis("bluetrophy")), value="6")
        ],
        placeholder=f"📁 {translate('sort_type', ctx)}",  # the placeholder text to show when no options have been chosen
        min_values=1,  # the minimum number of options a user must select
        max_values=1,  # the maximum number of options a user can select
    )
    selects = disnake.ui.ActionRow()
    selects.append_item(select)

    if length == 1:
        return [selects]

    page_buttons = [
        disnake.ui.Button(label="", emoji=partial_emoji_gen(bot, fetch_emojis("back")), style=disnake.ButtonStyle.grey,
                          disabled=(current_page == 0),
                          custom_id="Previous"),
        disnake.ui.Button(label=f"Page {current_page + 1}/{length}", style=disnake.ButtonStyle.grey,
                          disabled=True),
        disnake.ui.Button(label="", emoji=partial_emoji_gen(bot, fetch_emojis("forward")),
                          style=disnake.ButtonStyle.grey,
                          disabled=(current_page == length - 1), custom_id="Next")
    ]

    buttons = disnake.ui.ActionRow()
    for button in page_buttons:
        buttons.append_item(button)

    return [selects, buttons]
