import configs
import utils

import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_(url, fetch_name = None, retries = 3):
    if retries > 0:
        r = requests.get(url)
        if r.status_code == 200:
            res = r.json()
            return res
        elif r.status_code == 429: # Rate limit exceeded
            time.sleep(10)             
            return get_(url, fetch_name, retries = retries - 1)

def get_puuid(game_name = None, tagline = None):
    if game_name is not None and tagline is not None:
        retries = 5  # Maximum number of retries
        delay = 30  # Delay between retries in seconds

        for attempt in range(retries):
            try:
                r = get_(url=configs.ACCOUNT_BY_RIOT_ID.format(game_name=game_name, tagline=tagline), fetch_name=f"get_summoner for puuid (summoner): {game_name} {tagline}")
                if r is not None:
                    return r
                else:
                    raise ValueError("Received None response from one or more API calls")
            
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt == retries - 1:
                    logging.critical("Max retries reached. Could not fetch the data.")
                else:
                    logging.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)

def get_summoner(puuid = None, riot_id = None, account_id = None, summoner_id = None):
    """Returns a dictionary {id, accountId, puuid, name, profileIconId, revisionDate, summonerLevel}."""
    if puuid is not None:
        retries = 5  # Maximum number of retries
        delay = 30  # Delay between retries in seconds

        for attempt in range(retries):
            try:
                logging.info(f"Attempt {attempt + 1}: Fetching summoner data for puuid {puuid}...")
                
                # Try fetching summoner and account data
                r = get_(url=configs.SUMMONER_BY_PUUID.format(puuid=puuid), fetch_name=f"get_summoner for puuid (summoner): {puuid}")
                rr = get_(url=configs.ACCOUNT_BY_PUUID.format(puuid=puuid), fetch_name=f"get_summoner for puuid (account): {puuid}")
                
                if r is not None and rr is not None:
                    r.update(rr)
                    logging.info(f"Successfully fetched and merged data for puuid: {puuid}")
                    return r
                else:
                    logging.warning(f"Received None response for puuid: {puuid}")
                    raise ValueError("Received None response from one or more API calls")
            
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt == retries - 1:
                    logging.critical("Max retries reached. Could not fetch the data.")
                    raise  # This will re-raise the exception to propagate it after logging.
                else:
                    logging.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
    elif riot_id is not None:
        r  = get_(url = configs.ACCOUNT_BY_RIOT_ID.format(game_name = riot_id["game_name"], tagline = riot_id["tagline"]), fetch_name = f"get_summoner for riot_id: {riot_id}")
        return r
    elif account_id is not None:
        r  = get_(url = configs.SUMMONER_BY_ACCOUNT_ID.format(account_id = account_id), fetch_name = f"get_summoner for account_id: {account_id}")
        return r
    elif summoner_id is not None:
        r  = get_(url = configs.SUMMONER_BY_SUMMONER_ID.format(summoner_id = summoner_id), fetch_name = f"get_summoner for summoner_id: {summoner_id}")
        return r
    else:
        return None


def get_summoner_entries(summoner_id, tft = False):
    """Returns a dictionary of dictionaries {queue_type: dictionary about this queue_type}."""
    base_url = configs.ENTRY_BY_SUMMONER_ID if not tft else configs.TFT_ENTRY_BY_SUMMONER_ID
    r = get_(url = (base_url).format(summoner_id = summoner_id), fetch_name = "summoner_ranks")
    if r is not None:
        ranks = {}
        # r is a list (each entry corresponds to a queue)        
        for queue in r: 
            queue_type = queue["queueType"]
            ranks[queue_type] = queue
        return ranks
        

def get_played_games(puuid, queue_id, start, end, tft = False):
    """Return a list of match_ids corresponding to the (finished) games played by puuid between start and now (the beginning of the list is the most recent game)."""
    epoch_start = utils.convert_datetime_to_epoch(start)
    epoch_end = utils.convert_datetime_to_epoch(end)
    base_url = configs.MATCHES_BY_PUUID if not tft else configs.TFT_MATCHES_BY_PUUID
    r = get_(url = (base_url).format(puuid = puuid, epoch_start = epoch_start, epoch_end = epoch_end, queue_id = queue_id), fetch_name = "get_played_games")
    return r


def get_ended_game_info(match_id, tft = False):
    """Returns information about the ended game - the fields are detailled at https://developer.riotgames.com/apis#match-v5/GET_getMatch."""
    base_url = configs.MATCHES_BY_MATCH_ID if not tft else configs.TFT_MATCHES_BY_MATCH_ID
    r = get_(url = (base_url).format(match_id = match_id), fetch_name = "get_ended_game_info")
    return r


def get_current_game(puuid, tft = False):
    """Returns information about the current game."""
    base_url = configs.CURRENT_MATCH_BY_PUUID if not tft else configs.TFT_CURRENT_MATCH_BY_PUUID
    r = get_(url = (base_url).format(puuid = puuid), fetch_name = "get_current_game")
    return r


def get_apex_league(queue_id, apex_tier):
    """Returns information about the current game."""
    url = {"MASTER": configs.MASTER_LEAGUE_BY_QUEUE, 
          "GRANDMASTER": configs.GRANDMASTER_LEAGUE_BY_QUEUE,
          "CHALLENGER": configs.CHALLENGER_LEAGUE_BY_QUEUE}[apex_tier.upper()]
    r = get_(url = url.format(queue_type = configs.QUEUE_ID_TO_TYPE[str(queue_id)]), fetch_name = "get_apex_league")
    return r    

def get_cutoff(apex_tier, queue_id):
    """Gets the cutoff and a summoner at this cutoff for the apex_tier of the given queue_id."""

    # Load the 3 apex tiers (necessary regardless of the apex_tier queried)
    master = get_apex_league(queue_id, "MASTER")["entries"]
    grandmaster = get_apex_league(queue_id, "GRANDMASTER")["entries"]
    challenger = get_apex_league(queue_id, "CHALLENGER")["entries"]
    together = sorted(master + grandmaster + challenger, key = lambda participant: participant["leaguePoints"], reverse = True)

    # Get the cutoff
    if apex_tier.upper() in ["GM", "GRANDMASTER"]:
        participant = together[min(1000, len(together))] # Grandmaster tier has maximum 1000 players
        cutoff, summoner_id = max(participant["leaguePoints"], 200), participant["summonerId"] # Grandmaster tier needs 200+ LP
    elif apex_tier.upper() in ["CHALL", "CHALLENGER"]:
        participant = together[min(300, len(together))] # Challenger tier has maximum 300 players
        cutoff, summoner_id = max(participant["leaguePoints"], 500), participant["summonerId"] # Challenger tier needs 500+ LP

    return cutoff, summoner_id


def get_champion_mastery(summoner_id, champion_id):
    """Returns the mastery of this summoner for the given champion."""
    r = get_(url = configs.CHAMPION_MASTERY_BY_SUMMONER_ID.format(summoner_id = summoner_id, champion_id = champion_id), fetch_name = "get_champion_mastery")
    return r

