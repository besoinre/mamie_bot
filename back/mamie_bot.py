import configs
from game import Game
from change import Change
from summoner import Summoner
import utils

import json
import traceback
import riot_api
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class mamieBot():

    def __init__(self, queue_ids = ("1100")):
        self.queue_ids = queue_ids
        self.message_logs = []

        # Load the summoners from the local puuid list
        with open(configs.PUUID_PATH, encoding="utf-8") as json_data:
            data = json.load(json_data)
            self.gamename = list(data.keys()) 
            self.tagline = list(data.values())  
        self.puuids = []
        for game_name, tagline in zip(self.gamename, self.tagline):
            puuid = riot_api.get_puuid(game_name=game_name, tagline=tagline)
            self.puuids.append(puuid["puuid"])  

        self.summoners = {
            puuid: Summoner(puuid=puuid)
            for puuid in self.puuids
        }
        self.puuids = [summoner.puuid for summoner in self.summoners.values()]
        self.summoners_to_change = {puuid: Change(self.summoners[puuid], self.queue_ids) for puuid in self.puuids}
        self.summoners_to_games = {}
        self.game_ids_handled = [] # We keep track of the games that have ended and been handled to avoid duplicates


    # TODO: decay + decayed
    def update(self):
        logging.info(f"Running update()")

        self.message_logs = []
        for (puuid, summoner) in self.summoners.items():
            logging.info(f"Loop {summoner.game_name}")
            if self.summoners_to_games.get(puuid, []) == []:       
                changes = self.summoners_to_change[puuid].check_for_change() # TODO: refactor class Change() to be DecayChecker() and have it check for inactivity - add the dodge check to Dodge() class
                for (queue_id, change) in changes.items():
                        game_data = summoner.get_current_game()

                        if game_data is not None:
                            game = Game(game_data, summoner)
                            if game.game_id not in self.game_ids_handled: # The call summoner.get_current_game() lingers after the game ends so we check if it's a different game
                                message_log = game.tft_in_game_database_entry()
                                self.message_logs.append(message_log)
                                self.summoners_to_games[puuid] = [game]

            # Otherwise, we check if the game has ended (special case for TFT games as a summoner can get into another one while the previous one hasn't ended)
            else:
                games = self.summoners_to_games[puuid]
                for game in games:
                    
                    if game.has_ended():
                        logging.info(f"Game Ended")
                        message_log = game.tft_out_of_game_database_entry()
                        self.message_logs.append(message_log)
                        self.game_ids_handled.append(game.game_id)
                    else:
                        game_data = summoner.get_current_game()
                        if game_data is not None:
                            logging.info(f"Currently in game")
                            game = Game(game_data, summoner)
                            if (game.game_id not in self.game_ids_handled) and (game.game_id not in [game.game_id for game in games]):
                                message_log = game.tft_in_game_database_entry()
                                self.message_logs.append(message_log)
                                games.append(game)
                self.summoners_to_games[puuid] = [game for game in games if game.game_id not in self.game_ids_handled]