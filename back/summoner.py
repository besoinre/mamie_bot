import configs
import riot_api
import utils

import datetime
import pandas as pd


class Summoner:
    def __init__(self, puuid = None, riot_id = None, account_id = None, summoner_id = None):
        summoner = riot_api.get_summoner(puuid = puuid, riot_id = riot_id, account_id = account_id, summoner_id = summoner_id)
        if riot_id is None:
            if puuid is not None:
                self.puuid = summoner["puuid"]
                self.account_id = summoner["accountId"]
                self.summoner_id = summoner["id"]
                self.game_name = summoner["gameName"]
                self.tagline = summoner["tagLine"]            
            else:
                self.puuid = summoner["puuid"]
                self.account_id = summoner["accountId"]
                self.summoner_id = summoner["id"]
                self.game_name = None          
                self.tagline = None          
        else:
            self.puuid = summoner["puuid"]
            self.game_name = summoner["gameName"]
            self.tagline = summoner["tagLine"]
            summoner_bis = riot_api.get_summoner(puuid = self.puuid)
            self.account_id = summoner_bis["accountId"]
            self.summoner_id = summoner_bis["id"]            
        self.riot_name = f"{self.game_name}#{self.tagline}"
            
        
    def get_current_game(self, queue_id = "420"):
        """Returns None if the summoner is not in a queue_id game and otherwise returns the current game - we add the queue_id restriction to avoid mishaps with different queue_id games."""
        current_game = riot_api.get_current_game(self.puuid, tft = queue_id in configs.TFT_QUEUE_IDS)
        if current_game is not None and str(current_game["gameQueueConfigId"]) == str(queue_id):
                return current_game
        

    def get_played_games(self, queue_id = "420", start = utils.now() + datetime.timedelta(seconds = -3600*2), end = utils.now()):
        """Returns a list of all the queue_id games played in the selected queue in [start, now] - first game in the list is most recent one."""
        entries = riot_api.get_played_games(self.puuid, queue_id, start, end, tft = queue_id in configs.TFT_QUEUE_IDS)
        return entries if entries is not None else {}

    def get_all_played_games(self, queue_id = "420"):
        """Returns a list of all the queue_id games played since the beginning of the season."""
        timerange = pd.date_range(start = utils.string_to_datetime(ts = configs.BEGINNING_OF_SEASON, timezone = configs.TIMEZONE), end = utils.now() + datetime.timedelta(days = +1)) # Add one day because of 1pm start
        step = 5 # We take a 5 day step as we can only query 100 games at a time (ie 20 games a day)
        game_ids = []
        for i in range(0, len(timerange), step):
            start = timerange[i]
            end = timerange[min(i + step, len(timerange) - 1)]
            game_ids += self.get_played_games(queue_id, start, end)
        tft = queue_id in configs.TFT_QUEUE_IDS
        games = [riot_api.get_ended_game_info(game_id, tft = tft) for game_id in game_ids]   
        return games


    def get_last_played_game(self, queue_id = "420"):
        """Returns the last game played."""
        game_ids = self.get_played_games(queue_id, start = utils.string_to_datetime(ts = configs.BEGINNING_OF_SEASON, timezone = configs.TIMEZONE), end = utils.now())
        if game_ids:
            return riot_api.get_ended_game_info(game_ids[0], tft = queue_id in configs.TFT_QUEUE_IDS)


    def get_all_entries(self, tft = False):
        """Returns a dictionary of entries."""
        entries = riot_api.get_summoner_entries(self.summoner_id, tft=tft)
        return entries if entries is not None else {}
        

    def get_entry(self, queue_id = "420"):
        """Returns a dictionary {"tier": tier, "rank": rank, ...} about this queue_id."""
        tft = queue_id in configs.TFT_QUEUE_IDS
        all_ranks = self.get_all_entries(tft = tft)
        for queue_type in all_ranks:
            if configs.QUEUE_TYPE_TO_ID.get(queue_type) == str(queue_id):
                return all_ranks[queue_type]

        # If we reach this part it means the queue_type we want is not present in all_ranks: the summoner is unranked in that queue_type so we build the entry ourselves
        game_ids = self.get_played_games(queue_id, start = utils.string_to_datetime(ts = configs.BEGINNING_OF_SEASON, timezone = configs.TIMEZONE), end = utils.now())
        number_of_wins = 0
        progress = ""
        if game_ids:
            # Loop through the game_ids in reverse order as game_ids[0] is the most recent game played
            for game_id in game_ids[::-1]: 
                game_info = riot_api.get_ended_game_info(game_id, tft = tft)
                if game_info is not None:     
                    for participant in game_info["info"]["participants"]:
                        if participant["puuid"] == self.puuid:
                            progress += "W" if participant["win"] else "L"
                            number_of_wins += participant["win"]
        number_placements = configs.PLACEMENT_NUMBER if not tft else configs.TFT_PLACEMENT_NUMBER
        progress = progress.ljust(number_placements, "N") # Fill right end with "N"'s
        placements = {"target": number_placements, "wins": number_of_wins, "losses": len(game_ids) - number_of_wins, "progress": progress}
                  
        return {"leagueId": None, "queueType": configs.QUEUE_ID_TO_TYPE[str(queue_id)], "tier": "UNRANKED", "rank": "UNRANKED", "summonerId": self.summoner_id, 
                "summonerName": None, "leaguePoints": "UNRANKED", "wins": number_of_wins, "losses": len(game_ids) - number_of_wins, "veteran": None,  # summonerName is obsolete now
                "inactive": None, "freshBlood": None, "hotStreak": None,"placements": placements}