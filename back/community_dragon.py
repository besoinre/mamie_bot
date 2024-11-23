import requests


####################
# COMMUNITY DRAGON ENTRY POINTS (see https://github.com/communitydragon/docs/blob/master/assets.md)
####################


BASE_URL_CDRAGON = "https://raw.communitydragon.org/latest"
SUMMONER_SPELLS = f"{BASE_URL_CDRAGON}/plugins/rcp-be-lol-game-data/global/default/v1/summoner-spells.json"
CHAMPIONS = f"{BASE_URL_CDRAGON}/plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json"
TFT_MISC = f"{BASE_URL_CDRAGON}/plugins/rcp-be-lol-game-data/global/default/v1/tftitems.json"
TTF_CHAMPIONS = f"{BASE_URL_CDRAGON}/plugins/rcp-be-lol-game-data/global/default/v1/tftchampions.json"

####################
# MAPS
####################


SUMMONER_SPELLS_ID_TO_PATH_AND_NAME = {ss["id"] : {"path": ss["iconPath"].lower(), "name": ss["name"]} for ss in requests.get(url = SUMMONER_SPELLS).json()}
CHAMPION_ID_TO_PATH_AND_NAME = {champ["id"] : {"path": champ["squarePortraitPath"].lower(), "name": champ["name"]} for champ in requests.get(url = CHAMPIONS).json()}
TFT_MISC_ID_TO_PATH_AND_NAME = {misc["nameId"] : {"path": misc["squareIconPath"].lower(), "name": misc["name"]} for misc in requests.get(url = TFT_MISC).json()}
TFT_CHAMPIONS_ID_TO_PATH_AND_NAME = {champ["character_record"]["character_id"] : {"path": champ["character_record"]["squareIconPath"].lower(), "traits": [trait["name"] for trait in champ["character_record"]["traits"]]} for champ in requests.get(url = TTF_CHAMPIONS).json()}


####################
# FUNCTIONS
####################


def get_content_at_path(path, tft = False):
    """Returns the content at path by sourcing the correct url - see https://github.com/CommunityDragon/Docs/blob/master/assets.md#mapping-paths-from-json-files"""
    if not tft:
        real_path = path.split("assets/")[1]
        url = f"{BASE_URL_CDRAGON}/plugins/rcp-be-lol-game-data/global/default/{real_path}"
    else:
        real_path = path.split("assets/")[2]
        url = f"{BASE_URL_CDRAGON}/plugins/rcp-be-lol-game-data/global/default/assets/{real_path}"
    r = requests.get(url = url)
    if r.status_code == 200:
        content = r.content
        return content
    else:
        print(f"Error {r.status_code} while fetching get_content_at_path for {path}")


def get_pickrates():
    """Returns a dictionary {champion_id: {role: pickrate}} - code from https://github.com/meraki-analytics/role-identification/blob/master/roleidentification/pull_data.py."""
    url = "http://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/championrates.json"
    data = requests.get(url).json()["data"] # This is a nested map {str(champ_id): {role: {"playRate": pickrate in %}}}
    res =  {} # We build the map {int(champion_id): {role: pickrate}}
    for champion_id in data:
        data_champion_id = data[champion_id]
        res[int(champion_id)] = {role: useless_dict["playRate"] for (role, useless_dict) in data_champion_id.items()} # Cast champion_ids as int to be compliant with Riot api
    return res


PICKRATES = get_pickrates()


####################
# MISC
####################


MISSING_PING = requests.get(f"{BASE_URL_CDRAGON}/game/data/images/ui/pingmia.png").content
TFT_STAR = requests.get(f"{BASE_URL_CDRAGON}/game/assets/maps/particles/tft/tft_ui_star_silver.png").content
