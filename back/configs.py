####################
# API ENTRY POINTS
####################
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
TFT_API_KEY = os.getenv("API_KEY")
REGION = "euw1"
BASE_URL = "https://{region}.api.riotgames.com/lol".format(region = REGION)
BASE_URL_MATCH = "https://{region}.api.riotgames.com/lol".format(region = "europe")
BASE_URL_RIOT = "https://{region}.api.riotgames.com/riot".format(region = "europe")

SUMMONER_BY_PUUID = "{base}/summoner/v4/summoners/by-puuid/{{puuid}}?api_key={key}".format(base = BASE_URL, key = API_KEY)
# SUMMONER_BY_NAME = "{base}/summoner/v4/summoners/by-name/{{name}}?api_key={key}".format(base = BASE_URL, key = API_KEY) 
ACCOUNT_BY_PUUID = "{base}/account/v1/accounts/by-puuid/{{puuid}}?api_key={key}".format(base = BASE_URL_RIOT, key = API_KEY)
ACCOUNT_BY_RIOT_ID = "{base}/account/v1/accounts/by-riot-id/{{game_name}}/{{tagline}}?api_key={key}".format(base = BASE_URL_RIOT, key = API_KEY)
SUMMONER_BY_ACCOUNT_ID = "{base}/summoner/v4/summoners/by-account/{{account_id}}?api_key={key}".format(base = BASE_URL, key = API_KEY)
SUMMONER_BY_SUMMONER_ID = "{base}/summoner/v4/summoners/{{summoner_id}}?api_key={key}".format(base = BASE_URL, key = API_KEY)

ENTRY_BY_SUMMONER_ID = "{base}/league/v4/entries/by-summoner/{{summoner_id}}?api_key={key}".format(base = BASE_URL, key = API_KEY) # An entry is a dictionary about a ranked queue
MATCHES_BY_PUUID = "{base}/match/v5/matches/by-puuid/{{puuid}}/ids?startTime={{epoch_start}}&endTime={{epoch_end}}&queue={{queue_id}}&start=0&count=100&api_key={key}".format(base = BASE_URL_MATCH, key = API_KEY)
MATCHES_BY_MATCH_ID = "{base}/match/v5/matches/{{match_id}}?api_key={key}".format(base = BASE_URL_MATCH, key = API_KEY)
CURRENT_MATCH_BY_PUUID = "{base}/spectator/v5/active-games/by-summoner/{{puuid}}?api_key={key}".format(base = BASE_URL, key = API_KEY)
CHAMPION_MASTERY_BY_SUMMONER_ID = "{base}/champion-mastery/v4/champion-masteries/by-summoner/{{summoner_id}}/by-champion/{{champion_id}}?api_key={key}".format(base = BASE_URL, key = API_KEY)

MASTER_LEAGUE_BY_QUEUE = "{base}/league/v4/masterleagues/by-queue/{{queue_type}}?api_key={key}".format(base = BASE_URL, key = API_KEY)
GRANDMASTER_LEAGUE_BY_QUEUE = "{base}/league/v4/grandmasterleagues/by-queue/{{queue_type}}?api_key={key}".format(base = BASE_URL, key = API_KEY)
CHALLENGER_LEAGUE_BY_QUEUE = "{base}/league/v4/challengerleagues/by-queue/{{queue_type}}?api_key={key}".format(base = BASE_URL, key = API_KEY)

TFT_BASE_URL = "https://{region}.api.riotgames.com/tft".format(region = REGION)
TFT_BASE_URL_MATCH = "https://{region}.api.riotgames.com/tft".format(region = "europe")
TFT_ENTRY_BY_SUMMONER_ID = "{base}/league/v1/entries/by-summoner/{{summoner_id}}?api_key={key}".format(base = TFT_BASE_URL, key = TFT_API_KEY)
TFT_MATCHES_BY_PUUID = "{base}/match/v1/matches/by-puuid/{{puuid}}/ids?startTime={{epoch_start}}&endTime={{epoch_end}}&start=0&count=100&api_key={key}".format(base = TFT_BASE_URL_MATCH, key = TFT_API_KEY)
TFT_MATCHES_BY_MATCH_ID = "{base}/match/v1/matches/{{match_id}}?api_key={key}".format(base = TFT_BASE_URL_MATCH, key = TFT_API_KEY)
TFT_CURRENT_MATCH_BY_PUUID = "{base}/spectator/tft/v5/active-games/by-puuid/{{puuid}}?api_key={key}".format(base = BASE_URL, key = TFT_API_KEY) # This one goes through https://euw1.api.riotgames.com/lol/spectator/tft/v5/active-games/


####################
# DISCORD
####################


COMMAND_PREFIX = "!remi " # The trailing whitespace is important
GREEN_CHECKMARK = ":white_check_mark:"
RED_CROSS = ":x:"
WHITE_SQUARE = ":white_medium_square:"
BLACK_CIRCLE = ":black_circle:"
REGIONAL_INDICATOR_M = "\U0001F1F2" # From https://unicode-table.com/en/1F1F2/ - the pattern is "\U000{unicode_number}"
REGIONAL_INDICATOR_V = "\U0001F1FB"
REGIONAL_INDICATOR_P = "\U0001F1F5"
REGIONAL_INDICATOR_A = "\U0001F1E6" 
REGIONAL_INDICATOR_C = "\U0001F1E8"
REGIONAL_INDICATOR_E = "\U0001F1EA"
REGIONAL_INDICATOR_X = "\U0001F1FD"
REGIONAL_INDICATOR_D = "\U0001F1E9"
REGIONAL_INDICATOR_T = "\U0001F1F9"
REGIONAL_INDICATOR_O = "\U0001F1F4"
REGIONAL_INDICATOR_P = "\U0001F1F5"
DIGITS = [str("1️⃣"), str("2️⃣"), str("3️⃣"), str("4️⃣"), str("5️⃣"), str("6️⃣"), str("7️⃣"), str("8️⃣")]
STARS = ":star:"

####################
# COLOURS INT VALUE AND HEX CODE (from https://gist.github.com/thomasbnt/b6f455e2c7d743b796917fa3c205f812)
####################

ORANGE = 15105570 # #E67E22 - used for ingame
DARK_ORANGE = 11027200 # #A84300 - used for TFT ingame
GREEN = 5763719 # #57F287 - used for win
RED = 15548997 # #ED4245 - used for loss
YELLOW = 16776960 # #FFFF00 - used for bot conection
LIGHT_GREY = 12370112 # #BCC0C0 - used for dodge
BLACK = 2303786 # #23272A - used for remake
DARK_RED = 10038562 # #992D22 - used for decay
PURPLE = 10181046 #9B59B6 - used for dropping out of gm/chall
AQUA = 1752220	#1ABC9C - used for lp_update
NAVY = 3426654	#34495E - used for renames
DARK_BLUE = 2123412	#206694 - used for commands


####################
# RANKS
####################


APEX_TIERS = ["MASTER", "GRANDMASTER", "CHALLENGER"]
TIERS = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND"] + APEX_TIERS
RANKS = ["IV", "III", "II", "I"]
PLACEMENT_NUMBER = 5
TFT_PLACEMENT_NUMBER = 3


####################
# DECAY/DODGE
####################


DECAY_LP = {"DIAMOND": 50, "MASTER": 75, "GRANDMASTER": 75, "CHALLENGER": 75}
DECAY_DAYS = {"DIAMOND": 28, "MASTER": 14, "GRANDMASTER": 14, "CHALLENGER": 14}
FIRST_DODGE = {"lp_loss": 5, "timeout": 6*60} # -5 LP and 6 minute queue timeout
SECOND_DODGE = {"lp_loss": 15, "timeout": 30*60} # -15 LP and 30 minute queue timeout
THIRD_DODGE = {"lp_loss": 15, "timeout": 12*60*60} # -15 LP and 12 hours queue timeout
DODGE_TIER_DROP = 12*60*60 # 12 hours (the dodge tiers go down by 1 every 12 hours - see https://support-leagueoflegends.riotgames.com/hc/en-us/articles/201751844-Queue-Dodging)


####################
# SCORES
####################


METRICS = ["gold_earned", "kill_participation", "vision_score", "damage_buildings", "damage_objectives", "damage_to_champions", "level", "kda", "kills"]
WEIGHTS = {metric: 1/len(METRICS) for metric in METRICS}
ABSOLUTE_WEIGHT = 0.9
RELATIVE_WEIGHT = 1 - ABSOLUTE_WEIGHT


####################
# LOCAL FILES
####################


LP_UPDATE_PATH = "lp_update.txt"
PUUID_PATH = "puuid.txt"


####################
# MISC
####################


DMYHMS_FORMAT = "%d/%m/%Y, %H:%M:%S"
TFT_QUEUE_IDS = ["1100"]
QUEUE_TYPE_TO_ID = {"RANKED_SOLO_5x5": "420", "RANKED_TFT": "1100"}
QUEUE_ID_TO_TYPE = {value: key for (key, value) in QUEUE_TYPE_TO_ID.items()}
POSITION_TO_ROLE = {"TOP": "Top", "JUNGLE": "Jungle", "MIDDLE": "Mid", "BOTTOM": "Bot", "UTILITY": "Support", "UNKNOWN": "Unknown"}
BEGINNING_OF_SEASON = "19/07/2023, 13:00:00" # Relative to below timezone and in above format
BEGINNING_OF_SEASON = "10/01/2024, 13:00:00" # Relative to below timezone and in above format
BEGINNING_OF_SEASON = "15/05/2024, 13:00:00" # Relative to below timezone and in above format
TIMEZONE = "Europe/Paris"
TFT_REGEX = "-(i)+|_(i+)" # Captures either -i (or -ii, -iii), _i for augment tier