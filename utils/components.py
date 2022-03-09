import disnake

def create_components(current_page, embeds):
    length = len(embeds)
    if length == 1:
        return []

    page_buttons = [
        disnake.ui.Button(label="", emoji="◀️", style=disnake.ButtonStyle.blurple, disabled=(current_page == 0),
                          custom_id="Previous"),
        disnake.ui.Button(label=f"Page {current_page + 1}/{length}", style=disnake.ButtonStyle.grey,
                          disabled=True),
        disnake.ui.Button(label="", emoji="▶️", style=disnake.ButtonStyle.blurple,
                          disabled=(current_page == length - 1), custom_id="Next")
        ]
    buttons = disnake.ui.ActionRow()
    for button in page_buttons:
        buttons.append_item(button)

    return [buttons]