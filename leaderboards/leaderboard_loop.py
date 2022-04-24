
from disnake.ext import commands, tasks
from utils.helper import coc_client, ongoing_stats

locations = [32000007, 32000008, 32000009, 32000010, 32000011, 32000012, 32000013, 32000014, 32000015, 32000016, 32000017,
             32000018, 32000019, 32000020, 32000021, 32000022, 32000023, 32000024, 32000025, 32000026, 32000027, 32000028,
             32000029, 32000030, 32000031, 32000032, 32000033, 32000034, 32000035, 32000036, 32000037, 32000038, 32000039,
             32000040, 32000041, 32000042, 32000043, 32000044, 32000045, 32000046, 32000047, 32000048, 32000049, 32000050,
             32000051, 32000052, 32000053, 32000054, 32000055, 32000056, 32000057, 32000058, 32000059, 32000060, 32000061,
             32000062, 32000063, 32000064, 32000065, 32000066, 32000067, 32000068, 32000069, 32000070, 32000071, 32000072,
             32000073, 32000074, 32000075, 32000076, 32000077, 32000078, 32000079, 32000080, 32000081, 32000082, 32000083,
             32000084, 32000085, 32000086, 32000087, 32000088, 32000089, 32000090, 32000091, 32000092, 32000093, 32000094,
             32000095, 32000096, 32000097, 32000098, 32000099, 32000100, 32000101, 32000102, 32000103, 32000104, 32000105,
             32000106, 32000107, 32000108, 32000109, 32000110, 32000111, 32000112, 32000113, 32000114, 32000115, 32000116,
             32000117, 32000118, 32000119, 32000120, 32000121, 32000122, 32000123, 32000124, 32000125, 32000126, 32000127,
             32000128, 32000129, 32000130, 32000131, 32000132, 32000133, 32000134, 32000135, 32000136, 32000137, 32000138,
             32000139, 32000140, 32000141, 32000142, 32000143, 32000144, 32000145, 32000146, 32000147, 32000148, 32000149,
             32000150, 32000151, 32000152, 32000153, 32000154, 32000155, 32000156, 32000157, 32000158, 32000159, 32000160,
             32000161, 32000162, 32000163, 32000164, 32000165, 32000166, 32000167, 32000168, 32000169, 32000170, 32000171,
             32000172, 32000173, 32000174, 32000175, 32000176, 32000177, 32000178, 32000179, 32000180, 32000181, 32000182,
             32000183, 32000184, 32000185, 32000186, 32000187, 32000188, 32000189, 32000190, 32000191, 32000192, 32000193,
             32000194, 32000195, 32000196, 32000197, 32000198, 32000199, 32000200, 32000201, 32000202, 32000203, 32000204,
             32000205, 32000206, 32000207, 32000208, 32000209, 32000210, 32000211, 32000212, 32000213, 32000214, 32000215,
             32000216, 32000217, 32000218, 32000219, 32000220, 32000221, 32000222, 32000223, 32000224, 32000225, 32000226,
             32000227, 32000228, 32000229, 32000230, 32000231, 32000232, 32000233, 32000234, 32000235, 32000236, 32000237,
             32000238, 32000239, 32000240, 32000241, 32000242, 32000243, 32000244, 32000245, 32000246, 32000247, 32000248,
             32000249, 32000250, 32000251, 32000252, 32000253, 32000254, 32000255, 32000256, 32000257, 32000258, 32000259, 32000260]

rankings = []

class LeaderboardLoop(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.lbloop.start()


    def cog_unload(self):
        self.lbloop.cancel()


    @tasks.loop(seconds=300)
    async def lbloop(self):
        try:
            glob = await coc_client.get_location_players()
            x = 1
            global rankings
            rr = []
            for player in glob:
                rr.append(player.tag)
                rr.append("global")
                rr.append(x)
                rr.append("Global")
                try:
                    rr.append(player.clan.tag)
                    rr.append(player.clan.name)
                except:
                    rr.append("No Clan")
                    rr.append("No Clan")
                rr.append(player.trophies)
                rr.append(player.name)
                x += 1

            for location in locations:
                country = await coc_client.get_location_players(location_id=location)
                country_code = await coc_client.get_location(location_id=location)
                country_name = country_code.name
                # print(country_name)
                country_code = country_code.country_code
                x = 1
                for player in country:
                    rr.append(player.tag)
                    rr.append(country_code)
                    rr.append(x)
                    rr.append(country_name)
                    await ongoing_stats.update_one({'tag': f"{player.tag}"},
                                                   {'$set': {'location': country_name, "location_code": country_code}})
                    try:
                        rr.append(player.clan.tag)
                        rr.append(player.clan.name)
                    except:
                        rr.append("No Clan")
                        rr.append("No Clan")
                    rr.append(player.trophies)
                    rr.append(player.name)
                    x += 1
            rankings = rr

            print("lb loop done")
        except:
            pass


    @lbloop.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(LeaderboardLoop(bot))
