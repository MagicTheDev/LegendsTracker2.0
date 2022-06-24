
from disnake.ext import commands
import disnake
from collections import defaultdict
from utils.components import create_components

check = ["MainCheck", "Poster"]
track = ["Track"]
stats = ["MainStats"]
leaderboards = ["Leaderboards"]
settings = ["bot_settings"]
other = ["pepe", "help", "Patreon"]

pages = [check, track, stats, leaderboards, settings,  other]
page_names = ["Check", "Track", "Stats", "Leaderboards", "Settings", "Other"]

class help(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name='invite',
                       description="Invite for bot.")
    async def invite(self, ctx):
        await ctx.send("https://discord.com/api/oauth2/authorize?client_id=825324351016534036&permissions=2147747840&scope=bot%20applications.commands")

    @commands.slash_command(name='server',
                       description="Support server for bot.")
    async def serv(self, ctx):
        await ctx.send(
            "discord.gg/gChZm3XCrS")

    @commands.slash_command(name="quick_start", description="Guide with tips & basic commands to get started")
    async def quick_start(self, ctx: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(title="Getting Started",
                              color=disnake.Color.green())
        embed.add_field(name="Checking & Tracking Players", value=
                        "Players have to be tracked before they can be checked, a lot of players are already tracked however, but you can server track them to add them to your server"
                        " leaderboards, statistics, and feed. To do so, use `/track add`. If one by one isn't your style, you can bulk add with the `/ctrack` or `/country track` commands."
                        " With `/ctrack`, once you have linked clans to your server you can refresh your list of tracked players (putting them in sync) with `/ctrack sync`", inline=False)
        embed.add_field(name="Feeds", value="There are 2 types of feeds - the main feed & clan feeds. The main feed will show stats for any server tracked players & the clan feed will show stats"
                        " for the members in the respective clan - you can have 1 main feed & 5 clan feeds per a server. `/feed set` & `/clan-feed add` are the respective commands", inline=False)
        embed.add_field(name="Other", value="There are plenty of other stats & little nuiances to learn, enjoy, & explore. the `/faq` & `/help` commands are a great place to start & if you have any questions"
                                            " or suggestions to stop by the support server with `/server`", inline=False)
        await ctx.send(embed=embed)

    @commands.slash_command(name="faq", description="Frequently asked questions & their answers")
    async def faq(self, ctx: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(title="Frequently Asked Questions",
                              color=disnake.Color.green())
        embed.add_field(name="**Q: I just tracked a player. Why is there no stats?**",
                        value="A. Legends stats aren't given outright, so they have to be collected as they happen. Stats will appear from the moment tracked forward.", inline=False)
        embed.add_field(name="**Q: THE STATS ARE WRONG ?!**", value="A: Well it depends. One, it helps to understand how this bot works, as mentioned above, there can be errors, why is that? "
                              "The api doesn’t give legends stats. This bot works by checking player's trophies non-stop. If the trophies go up, it’s an attack. If they go down, it’s a defense. Sounds good, except, the api doesn’t update immediately, it takes 3 to 5 minutes on average. In those few minutes, the trophies (how we’re checking hits/defenses) could change in a few ways that can trip up the bot. 1. 2 attacks in a short time frame, "
                              "in this case you will see stats like +68, that’s just 2 hits, & tbh it’s 100% accurate for all intents & purposes. 2. 2 defenses happen at same time, same as above but something like -68. And Lastly, 3,  where we can get some inaccuracy, a defense & attack happen at same time, u may get something like +4 if a +30 attack & -26 defense happen at same time. Always, the net gain/loss for the day will be accurate ", inline=False)
        embed.add_field(name="**Q: Where is this months history?**",
                        value="A: The monthly history has to be downloaded in bulk - it contains about 700 thousand records on average. It also doesn't become available till several days after season ends. I try to download it & add it as soon as I can.", inline=False)
        embed.add_field(name="**Q: Why doesn’t an account show country?**",
                        value="A. The bot has never seen the player in the top 200 in a location or region")
        await ctx.send(embed=embed)

    @commands.slash_command(name='help', description="List of commands & descriptions for LegendsTracker")
    async def help(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.response.defer()
        cog_dict = defaultdict(list)
        command_description = {}
        for command in self.bot.slash_commands:
            cog_name = command.cog_name
            base_command = command.name
            children = command.children
            if children != {}:
                for child in children:
                    command = children[child]
                    full_name = f"{base_command} {command.name}"
                    # for option in command.body.options:
                    # full_name += f" [{option.name}]"
                    cog_dict[cog_name].append(full_name)
                    desc = command.body.description
                    command_description[full_name] = desc
            else:
                desc = command.description
                # for option in command.body.options:
                # base_command += f" [{option.name}]"
                command_description[base_command] = desc
                cog_dict[cog_name].append(base_command)

        embeds = []
        x = 0
        for page in pages:
            embed = disnake.Embed(title=page_names[x],
                                  color=disnake.Color.green())
            embed.set_footer(text=f"{len(command_description)} commands")
            for cog in page:
                text = ""
                commands = cog_dict[cog]
                for command in commands:
                    description = command_description[command]
                    if len(text) + len(f"`/{command}`\n{description}\n") >= 1020:
                        embed.add_field(name=cog, value=text, inline=False)
                        text = ""
                    text += f"`/{command}`\n{description}\n"
                embed.add_field(name=cog, value=text, inline=False)
            embeds.append(embed)
            x += 1
        current_page = 0
        await ctx.edit_original_message(embed=embeds[0], components=create_components(self.bot, current_page, embeds, True))
        msg = await ctx.original_message()

        def check(res: disnake.MessageInteraction):
            return res.message.id == msg.id

        while True:
            try:
                res: disnake.MessageInteraction = await self.bot.wait_for("message_interaction", check=check,
                                                                          timeout=600)
            except:
                await msg.edit(components=[])
                break

            if res.data.custom_id == "Previous":
                current_page -= 1
                await res.response.edit_message(embed=embeds[current_page],
                                                components=create_components(self.bot, current_page, embeds, True))

            elif res.data.custom_id == "Next":
                current_page += 1
                await res.response.edit_message(embed=embeds[current_page],
                                                components=create_components(self.bot, current_page, embeds, True))

            elif res.data.custom_id == "Print":
                await msg.delete()
                for embed in embeds:
                    await ctx.channel.send(embed=embed)




def setup(bot: commands.Bot):
    bot.add_cog(help(bot))
