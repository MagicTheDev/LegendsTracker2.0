
from disnake.ext import commands
import disnake
from utils.helper import getPlayer, ongoing_stats, profile_db
stat_types = ["Yesterday Legends", "Legends Overview", "Graph & Stats", "Add to Quick Check"]


class FeedButtons(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
      

    @commands.Cog.listener()
    async def on_button_click(self, ctx: disnake.MessageInteraction):
        if ctx.component.label == "All Stats":
            tag = ctx.component.custom_id
            results = []
            results.append(tag)

            check = self.bot.get_cog("MainCheck")
            current_page = 0
            stats_page = []
            trophy_results = []
            x = 0
            for result in results:
                r = await ongoing_stats.find_one({"tag": result})
                name = r.get("name")
                trophies = r.get("trophies")
                trophy_results.append(disnake.SelectOption(label=f"{name} | 🏆{trophies}", value=f"{x}"))
                embed = await check.checkEmbed(result)
                stats_page.append(embed)
                x += 1

            components = await self.create_components(results, trophy_results)
            await ctx.send(embed=stats_page[0], components=components, delete_after=300)
            msg = await ctx.original_message()

            def check(res: disnake.MessageInteraction):
                return res.message.id == msg.id

            while True:
                try:
                    res: disnake.MessageInteraction = await self.bot.wait_for("message_interaction", check=check,
                                                                              timeout=120)
                except:
                    break


                if res.values[0] in stat_types:
                    if res.values[0] == "Add to Quick Check":
                        await self.add_profile(res, results[current_page], components, msg)
                    else:
                        await res.response.defer()
                        current_stat = stat_types.index(res.values[0])
                        embed = await self.display_embed(results, stat_types[current_stat], current_page, ctx)
                        await msg.edit(embed=embed,
                                       components=components)


    async def add_profile(self, res, tag, components, msg):
        results = await profile_db.find_one({'discord_id': res.author.id})
        await msg.edit(components=components)
        if results is None:
            await profile_db.insert_one({'discord_id': res.author.id,
                                         "profile_tags" : [f"{tag}"]})
            player = await getPlayer(tag)
            await res.send(content=f"Added {player.name} to your Quick Check list.", ephemeral=True)
        else:
            profile_tags = results.get("profile_tags")
            if tag in profile_tags:
                await profile_db.update_one({'discord_id': res.author.id},
                                               {'$pull': {"profile_tags": tag}})
                player = await getPlayer(tag)
                await res.send(content=f"Removed {player.name} from your Quick Check list.", ephemeral=True)
            else:
                if len(profile_tags) > 25:
                    await res.send(content=f"Can only have 25 players on your Quick Check list. Please remove one.", ephemeral=True)
                else:
                    await profile_db.update_one({'discord_id': res.author.id},
                                               {'$push': {"profile_tags": tag}})
                    player = await getPlayer(tag)
                    await res.send(content=f"Added {player.name} to your Quick Check list.", ephemeral=True)


    async def display_embed(self, results, stat_type, current_page, ctx):

        check = self.bot.get_cog("MainCheck")

        if stat_type == "Legends Overview":
            return await check.checkEmbed(results[current_page])
        elif stat_type == "Yesterday Legends":
            return await check.checkYEmbed(results[current_page])
        elif stat_type == "Graph & Stats":
            return await check.createGraphEmbed(results[current_page])
        elif stat_type == "Legends History":
            return await check.create_history(ctx, results[current_page])

    async def create_components(self, results, trophy_results):
        length = len(results)

        options = []

        for stat in stat_types:
            if stat == "Add to Quick Check":
                options.append(disnake.SelectOption(label=f"{stat}", value=f"{stat}", description="(If already added, will remove player instead)"))
            else:
                options.append(disnake.SelectOption(label=f"{stat}", value=f"{stat}"))

        stat_select  = disnake.ui.Select(
            options=options,
            placeholder="Stat Pages & Settings",
            min_values=1,  # the minimum number of options a user must select
            max_values=1  # the maximum number of options a user can select
        )
        st = disnake.ui.ActionRow()
        st.append_item(stat_select)

        if length == 1:
            return st

        profile_select = disnake.ui.Select(
            options=trophy_results,
            placeholder="Player Results",
            min_values=1,  # the minimum number of options a user must select
            max_values=1  # the maximum number of options a user can select
        )
        st2 = disnake.ui.ActionRow()
        st2.append_item(profile_select)

        return[st, st2]

def setup(bot):
    bot.add_cog(FeedButtons(bot))
