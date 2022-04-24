import coc
from coc import utils
from utils.helper import ongoing_stats, server_db
from datetime import datetime
import pytz
utc = pytz.utc

class CustomPlayer(coc.Player):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def is_legend(self):
        if str(self.league) != "Legend League":
            return False
        return True

    ##STRAIGHT DB VALUES
    def db_name(self, player):
        return player.get("name")

    def db_league(self, player):
        return player.get("league")

    def db_clan_name(self, player):
        return player.get("clan")

    def db_clan_tag(self, player):
        return player.get("clan_tag")

    def db_th_lvl(self, player):
        return player.get("th")

    def db_link(self, player):
        return player.get("link")

    def db_trophies(self, player):
        return player.get("trophies")

    def db_clan_badge_link(self, player):
        return player.get("badge")

    def db_todays_hits(self, player):
        return player.get("today_hits")

    async def get_todays_hits(self):
        results = await ongoing_stats.find_one({"tag": f"{self.tag}"})
        return results.get("today_hits")

    def db_today_defs(self, player):
        return player.get("today_defenses")

    def db_season_hits(self, player):
        return int(player.get("num_season_hits"))

    def db_season_defs(self, player):
        return int(player.get("num_season_defenses"))

    async def db_last_update(self, player):
        last_update = player.get("last_update")
        if last_update is None:
            dt = datetime.now(utc)
            utc_time = dt.replace(tzinfo=utc)
            utc_timestamp = utc_time.timestamp()
            await ongoing_stats.update_one({'tag': f"{self.tag}"},
                                           {'$set': {'last_update': utc_timestamp}})
            return utc_timestamp

        return last_update

    def db_location(self, player):
        return player.get("location")

    def db_location_code(self, player):
        return player.get("location_code")

    async def db_current_streak(self):
        results = await ongoing_stats.find_one({"tag": f"{self.tag}"})
        numberOfTriples = results.get("row_triple")
        return numberOfTriples

    def db_highest_streak(self, player):
        highest_streak = player.get("highest_streak")
        if highest_streak is None:
            highest_streak = 0
        return highest_streak

    def db_get_changes(self, player):
        return player.get("change")



    #PURE DB EXTENSION METHODS
    def db_num_hits(self, player):
        return player.get("num_today_hits")

    def db_num_def(self, player):
        defs = player.get("today_defenses")
        return(len(defs))

    def db_sum_hits(self, player):
        hits = player.get("num_today_hits")
        return sum(hits)

    def db_sum_defs(self, player):
        defs = player.get("today_defenses")
        return sum(defs)

    def db_today_net(self, player):
        sum_hits = self.db_sum_hits(player)
        sum_defs = self.db_sum_defs(player)
        return sum_hits - sum_defs


    async def bot_rank(self, day):
        rankings = []
        tracked = ongoing_stats.find()
        limit = await ongoing_stats.count_documents(filter={})
        for document in await tracked.to_list(length=limit):
            tag = document.get("tag")
            if day == 0:
                trophy = document.get("trophies")
            else:
                record = day + 1
                eod = document.get("end_of_day")
                if record > len(eod):
                    continue
                trophy = eod[-record]
            rr = []
            rr.append(tag)
            rr.append(trophy)
            rankings.append(rr)

        ranking = sorted(rankings, key=lambda l: l[1], reverse=True)
        async def get_rank(tag, ranking):
            for i, x in enumerate(ranking):
                if tag in x:
                    return i
        ranking = await get_rank(self.tag, ranking)
        return str(ranking + 1)


    #SET/UPDATE DB METHODS
    async def update_clan_name(self, player):
        if self.clan_name != self.db_clan_name(player):
            await ongoing_stats.update_one({'tag': f"{self.tag}"}, {'$set': {'clan': f'{self.clan_name()}'}})

    async def update_clan_tag(self, player):
        if self.clan_tag != self.db_clan_tag(player):
            await ongoing_stats.update_one({'tag': f"{self.tag}"}, {'$set': {'clan_tag': f'{self.clan_tag()}'}})

    async def update_clan_badge(self, player):
        if self.clan_badge_link != self.db_clan_badge_link(player):
            await ongoing_stats.update_one({'tag': f"{self.tag}"}, {'$set': {'badge': f'{self.clan_badge_link()}'}})

    async def update_th(self, player):
        if self.town_hall != self.db_th_lvl(player):
            await ongoing_stats.update_one({'tag': f"{self.tag}"}, {'$set': {'th': self.town_hall}})

    async def update_name(self, player):
        if self.name != self.db_name(player):
            await ongoing_stats.update_one({'tag': f"{self.tag}"}, {'$set': {'name': f'{self.name}'}})

    async def update_league(self, player):
        if str(self.league) != player.get("league"):
            await ongoing_stats.update_one({'tag': f"{self.tag}"}, {'$set': {'league': f'{str(self.league)}'}})

    async def update_trophies(self, player):
        if self.trophies != self.db_trophies(player):
            await ongoing_stats.update_one({'tag': f"{self.tag}"}, {'$set': {'trophies': self.trophies}})

    async def set_last_update(self):
        dt = datetime.now(utc)
        utc_time = dt.replace(tzinfo=utc)
        utc_timestamp = utc_time.timestamp()
        await ongoing_stats.update_one({'tag': f"{self.tag}"},
                                       {'$set': {'last_update': utc_timestamp}})

    async def set_season_hits(self):
        await ongoing_stats.update_one({'tag': f"{self.tag}"}, {'$set': {'num_season_hits': self.attack_wins}})

    async def set_season_defs(self):
        await ongoing_stats.update_one({'tag': f"{self.tag}"}, {'$set': {'num_season_defenses': self.defense_wins}})

    async def increment_todays_hits(self):
        await ongoing_stats.update_one({'tag': f"{self.tag}"},
                                       {'$inc': {'num_today_hits': 1}})

    async def insert_attack(self, attack: int):
        await ongoing_stats.update_one({'tag': f"{self.tag}"},
                                       {'$push': {'today_hits': attack}})

    async def insert_defense(self, defense: int):
        await ongoing_stats.update_one({'tag': f"{self.tag}"},
                                       {'$push': {'today_defenses': defense}})

    async def increment_streak(self):
        await ongoing_stats.update_one({'tag': f"{self.tag}"},
                                       {'$inc': {'row_triple': 1}})

    async def reset_streak(self):
        await ongoing_stats.update_one({'tag': f"{self.tag}"},
                                       {'$set': {'row_triple': 0}})

    async def update_highest_streak(self):
        highest = await self.db_current_streak()
        await ongoing_stats.update_one({'tag': f"{self.tag}"},
                                       {'$set': {'highest_streak': highest}})

    async def remove_from_tracking(self):
        await ongoing_stats.find_one_and_delete({"tag": self.tag})


    #CONVENIENCE METHODS (USES COC API)

    def clan_badge_link(self):
        if self.clan is not None:
            return self.clan.badge.url
        else:
            return None

    def trophies_changed(self, player):
        previous_trophies = player.get("trophies")
        if previous_trophies < self.trophies:
            return self.trophies - previous_trophies
        elif previous_trophies > self.trophies:
            return self.trophies - previous_trophies
        else:
            return None

    def season_hit_change(self, player):
        return self.attack_wins - self.db_season_hits(player)

    def clan_name(self):
        current_clan = "No Clan"
        try:
            current_clan = self.clan.name
            return current_clan
        except:
            return current_clan

    def clan_tag(self):
        current_clan_tag = "No Clan"
        try:
            current_clan_tag = self.clan.tag
            return current_clan_tag
        except:
            return current_clan_tag


    #hitratees
    async def season_hit_stats(self, player):
        start = utils.get_season_start().replace(tzinfo=utc).date()
        now = datetime.utcnow().replace(tzinfo=utc).date()
        now_ = datetime.utcnow().replace(tzinfo=utc)
        current_season_progress = now - start
        current_season_progress = current_season_progress.days
        if now_.hour <= 5:
            current_season_progress -= 1
        first_record = 0
        last_record = current_season_progress
        y = player.get("end_of_day")

        len_y = len(y)
        if last_record == len_y:
            last_record -= 1
        if last_record > len_y:
            last_record = len(y) - 1

        if first_record >= len_y - 2:
            return None

        one_stars = 0
        two_stars = 0
        three_stars = 0

        zero_star_def = 0
        one_stars_def = 0
        two_stars_def = 0
        three_stars_def = 0

        hits = player.get("previous_hits")
        defs = player.get("previous_defenses")
        hits = hits[len(hits) - last_record:len(hits) - first_record]
        defs = defs[len(defs) - last_record:len(defs) - first_record]

        for day in hits:
            for hit in day:
                if hit >= 5 and hit <= 15:
                    one_stars += 1
                elif hit >= 16 and hit <= 32:
                    two_stars += 1
                elif hit >= 40:
                    if hit % 40 == 0:
                        three_stars += (hit // 40)

        total = one_stars + two_stars + three_stars
        try:
            one_stars_avg = int(round((one_stars / total), 2) * 100)
        except:
            one_stars_avg = 0
        try:
            two_stars_avg = int(round((two_stars / total), 2) * 100)
        except:
            two_stars_avg = 0
        try:
            three_stars_avg = int(round((three_stars / total), 2) * 100)
        except:
            three_stars_avg = 0

        for day in defs:
            for hit in day:
                if hit >= 0 and hit <= 4:
                    zero_star_def += 1
                if hit >= 5 and hit <= 15:
                    one_stars_def += 1
                elif hit >= 16 and hit <= 32:
                    two_stars_def += 1
                elif hit >= 40:
                    if hit % 40 == 0:
                        three_stars_def += (hit // 40)

        total_def = zero_star_def + one_stars_def + two_stars_def + three_stars_def
        try:
            zero_stars_avg_def = int(round((zero_star_def / total_def), 2) * 100)
        except:
            zero_stars_avg_def = 0
        try:
            one_stars_avg_def = int(round((one_stars_def / total_def), 2) * 100)
        except:
            one_stars_avg_def = 0
        try:
            two_stars_avg_def = int(round((two_stars_def / total_def), 2) * 100)
        except:
            two_stars_avg_def = 0
        try:
            three_stars_avg_def = int(round((three_stars_def / total_def), 2) * 100)
        except:
            three_stars_avg_def = 0

        return [one_stars_avg, two_stars_avg, three_stars_avg, one_stars_avg_def, two_stars_avg_def,
                three_stars_avg_def]



    #tracking methods
    async def is_server_tracked(self, server_id):
        results = await server_db.find_one({"server": server_id})
        tracked_members = results.get("tracked_members")

        results = await ongoing_stats.find_one({"tag": self.tag})
        if results is not None:
            servers = []
            servers = results.get("servers")
            if servers is None:
                servers = []
        else:
            servers = []

        return ((self.tag in tracked_members) or (server_id in servers))

    async def is_global_tracked(self):
        results = await ongoing_stats.find_one({"tag": f"{self.tag}"})
        return results is not None

    async def add_global_tracking(self):
        await ongoing_stats.insert_one({
            "tag": self.tag,
            "name": self.name,
            "trophies": self.trophies,
            "th": self.town_hall,
            "num_season_hits": self.attack_wins,
            "num_season_defenses": self.defense_wins,
            "row_triple": 0,
            "today_hits": [],
            "today_defenses": [],
            "num_today_hits": 0,
            "previous_hits": [],
            "previous_defenses": [],
            "num_yesterday_hits": 0,
            "servers": [],
            "end_of_day": [],
            "clan": self.clan_name(),
            "badge": self.clan_badge_link(),
            "link": self.share_link,
            "league": str(self.league),
            "highest_streak": 0,
            "last_updated": None,
            "change": None
        })

    async def add_server_tracking(self, guild_id):
        await ongoing_stats.update_one({'tag': self.tag},
                                       {'$push': {"servers": guild_id}})
        await server_db.update_one({'server': guild_id},
                                   {'$push': {"tracked_members": self.tag}})

    async def remove_server_tracking(self, guild_id):
        await ongoing_stats.update_one({'tag': self.tag},
                                       {'$pull': {"servers": guild_id}})
        await server_db.update_one({'server': guild_id},
                                   {'$pull': {"tracked_members": self.tag}})



