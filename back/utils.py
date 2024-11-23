import configs
import community_dragon as cdragon

import datetime
import pytz

from functools import reduce


####################
# TIME
####################


def add_time(f):
    """Decorator to add the time to a function f outputting a string."""
    def aux(*args, **kwargs):
        return "{dt}: {s}".format(dt = now().strftime(configs.DMYHMS_FORMAT), s = f(*args, **kwargs))
    return aux


def convert_datetime_to_epoch(dt):
    """Converts given datetime to an epoch timestamp in seconds (ie to the number of seconds between 1st Jan 1970 0:00 and dt)."""
    return int(dt.timestamp())


def convert_epoch_to_datetime(epoch, timezone = configs.TIMEZONE):
    """Converts given epoch timestamp in seconds to datetime."""
    return datetime.datetime.fromtimestamp(epoch).astimezone(pytz.timezone(timezone))


def convert_seconds_to_hms(n):
    """Converts a number of seconds to hour/minute/seconds."""
    h = int(n/3600)
    n -= 3600*h
    m = int(n/60)
    n -= 60*m
    s = n
    return f"{h:d}:{m:02d}:{s:02}" if h > 0 else f"{m:02d}:{s:02d}"


def now(timezone = configs.TIMEZONE):
    return datetime.datetime.now(pytz.timezone(timezone))


def string_to_datetime(ts, timezone = configs.TIMEZONE):
    """Converts a string to a datetime.datetime object."""
    res = datetime.datetime.strptime(ts, configs.DMYHMS_FORMAT) if ts is not None else now(timezone = timezone)
    res = res.astimezone(pytz.timezone(timezone))
    return res


####################
# ENTRY/PROGRESS
####################


def find_index(x, l):
    """Returns the index of the first ocurrence of x in l."""
    for i in range(0, len(l)):
        if l[i] == x:
            return i
    return -1


def number_to_entry(number):
    """Gives the corresponding entry to the number, starting from Iron IV 0 LP for 0."""
    rank_multiplier = 101 # 101 LP per rank (0 to 100)
    tier_multiplier = rank_multiplier*len(configs.RANKS)
    tier = configs.TIERS[min(number//tier_multiplier, len(configs.TIERS) - len(configs.APEX_TIERS))] # Default the tier to the lowest apex tier as LP alone can't differentiate between apex tiers
    rank = configs.RANKS[(number - (number//tier_multiplier)*tier_multiplier)//rank_multiplier] if tier not in configs.APEX_TIERS else "I"
    lp = number%rank_multiplier if tier not in configs.APEX_TIERS else number - entry_to_number({"tier": "Master", "rank": "IV", "leaguePoints": 0})
    return {"tier": tier, "rank": rank, "leaguePoints": lp}


def entry_to_number(entry):
    """Gives the corresponding number to the entry, starting from 0 for Iron IV 0 LP."""
    if entry["tier"] == "UNRANKED":
        return -1
    tier = entry["tier"].upper() # eg: Gold
    rank = entry["rank"] if tier not in configs.APEX_TIERS else "IV"
    lp = entry["leaguePoints"]
    rank_multiplier = 101 # 101 LP per rank (0 to 100)
    tier_multiplier = rank_multiplier*len(configs.RANKS)
    tier_index = find_index(tier, configs.TIERS) if tier not in configs.APEX_TIERS else (len(configs.TIERS) - len(configs.APEX_TIERS))
    number = tier_index*tier_multiplier + find_index(rank, configs.RANKS)*rank_multiplier + lp
    return number


def format_entry(entry):
    """Gets the rating (tier + rank + lp)."""
    tier = entry["tier"] # eg: Gold
    rank = entry["rank"] # eg: II
    tier_division = tier.capitalize() + ((" " + rank) if tier not in configs.APEX_TIERS else "") # "Master" instead of "Master I"
    lp = entry["leaguePoints"]
    if tier.upper() == "UNRANKED":
        progress = entry["placements"]["progress"]
        formatted_progress = format_progress(progress)
        res = f"Unranked ({formatted_progress})"
    else:
        res = f"{tier_division} {lp} LP"
    return res
                

def format_progress(progress):
    """Formats the progress string (eg "WLN") into Discord emojis."""
    res = ""
    for c in progress:
        if c == "W":
            res += configs.GREEN_CHECKMARK
        elif c == "L":
            res += configs.RED_CROSS
        elif c == "N":
            res += configs.WHITE_SQUARE
        elif c == "D":
            res += configs.BLACK_CIRCLE # Dodges
        else:
            res += c
    return res


def update_progress(progress, win = True):
    """Updates the progress string (eg adding a win to WNN yields WWN)."""
    res = ""
    for i in range(0, len(progress)):
        if progress[i] == "N":
            break
    return progress[:i] + ("W" if win else "L") + progress[i + 1:] # i + 1 to discard one "N" that's been repalce by "W" or "L"


def get_adjacent_entry(entry, get_next = True):
    """Gets the next/previous possible rating (ie Gold III _ LP -> Gold II 1 LP)."""
    tier = entry["tier"] # eg: Gold
    rank = entry["rank"] # eg: II
    # Tier promotion
    if (rank == "I" and get_next):
        next_tier = configs.TIERS[find_index(tier, configs.TIERS) + 1]
        next_rank = "IV" if next_tier not in configs.APEX_TIERS else "I"
        next_lp = 1
    # Tier demotion
    elif ((rank == "IV" or tier.upper() == "MASTER") and not get_next):
        next_tier = configs.TIERS[find_index(tier, configs.TIERS) - 1]
        next_rank = "I"
        next_lp = 75
    # Rank promotion/demotion
    else:
        next_tier = tier
        next_rank = configs.RANKS[find_index(rank, configs.RANKS) + (1 if get_next else -1)]
        next_lp = 1 if get_next else 75
            
    return {"tier": next_tier, "rank": next_rank, "leaguePoints": next_lp}


####################
# GAME METRICS
####################


def get_role_played(participants):
    """Gives the role played by each participant (the order of reliability seems to be teamPosition > individualPosition > lane)."""
    res = {}
    for participant in participants:
        position = participant["teamPosition"] 
        position = position if position != "" else participant["individualPosition"]
        position = position if position.upper() != "INVALID" else participant["lane"]
        position = position if position.upper() != "NONE" else "UNKNOWN"
        role = configs.POSITION_TO_ROLE[position] # The order of reliability seems to be teamPosition > individualPosition > lane
        res[participant["puuid"]] = role
    return res


def get_metrics(participant):
    """Extracts metrics from the given dictionary."""
    res = {}
    res["win"] = participant["win"]
    res["kills"] = participant["kills"]
    res["deaths"] = participant["deaths"]
    res["assists"] = participant["assists"]
    res["kda"] = (res["kills"] + res["assists"])/res["deaths"] if res["deaths"] != 0 else 0    
    res["kill_participation"] = participant["challenges"].get("killParticipation", 1) # killParticipation won't be present if the team scored 0 kills
    res["cs"] = participant["totalMinionsKilled"] + participant["neutralMinionsKilled"]
    res["vision_score"] = participant["visionScore"]
    res["gold_earned"] = participant["goldEarned"]
    res["damage_buildings"] = participant["damageDealtToBuildings"]
    res["damage_objectives"] = participant["damageDealtToObjectives"] - participant["damageDealtToBuildings"] # We want damage_objectives to be drake/herald/nashor
    res["level"] = participant["champLevel"]
    res["number_of_pings"] = participant["basicPings"]
    res["pentakills"] = participant["pentaKills"]
    res["team_id"] = participant["teamId"]            
    res["phsyical_damage_to_champions"] = participant["physicalDamageDealtToChampions"]            
    res["magic_damage_to_champions"] = participant["magicDamageDealtToChampions"]    
    res["true_damage_to_champions"] = participant["trueDamageDealtToChampions"]    
    res["damage_to_champions"] = participant["physicalDamageDealtToChampions"] + participant["magicDamageDealtToChampions"] + participant["trueDamageDealtToChampions"]
    return res


def compute_score(game_info, explained = False):
    """Gives a rating 0-10 to each player of the ended game."""

    # Get each summoner's metrics
    participants = game_info["participants"]
    puuids = set([participant["puuid"] for participant in participants])
    winners = [participant["puuid"] for participant in participants if participant["win"]]
    losers = [participant["puuid"] for participant in participants if not participant["win"]]
    puuid_to_role = get_role_played(participants)    
    puuid_to_champ_name = {puuid: [cdragon.CHAMPION_ID_TO_PATH_AND_NAME[participant["championId"]]["name"] for participant in participants if participant["puuid"] == puuid][0] for puuid in puuids}
    metrics_to_puuid = {metric: {participant["puuid"]: get_metrics(participant)[metric] for participant in participants} for metric in configs.METRICS}

    # Get each player's absolute score per metric: for a given metric, the scores are linearly distributed among [0, 10]
    absolute_scores_per_metric = {}
    for metric in metrics_to_puuid:
        performances = metrics_to_puuid[metric]
        max_perf = max(performances.values())
        min_perf = min(performances.values())
        slope = 10/(max_perf - min_perf) if max_perf != min_perf else 0 # The slope in f(perf) = slope*perf + intercept with f(max_perf) = 10 and f(min_perf) = 0
        intercept = 10 - slope*max_perf # The intercept in f(perf) = slope*perf + intercept with f(max_perf) = 10 and f(min_perf) = 0
        absolute_scores_per_metric[metric] = {puuid: slope*performances[puuid] + intercept for puuid in performances}

    # Get each player's relative rank score per metric: for a given metric, the differences winning - losing are linearly distributed among [0, 10]
    relative_scores_per_metric = {}
    for metric in metrics_to_puuid:
        performances = metrics_to_puuid[metric]
        differences = {}
        for role in puuid_to_role.values():
            winner = [winner for winner in winners if puuid_to_role[winner] == role][0]
            loser = [loser for loser in losers if puuid_to_role[loser] == role][0]
            differences[role] = performances[winner] - performances[loser]
        max_diff = max(differences.values())
        min_diff = min(differences.values())     
        slope = 10/(max_diff - min_diff) if max_diff != min_diff else 0 # The slope in f(diff) = slope*diff + intercept with f(max_diff) = 10 and f(min_diff) = 0
        intercept = 10 - slope*max_diff # The intercept in f(diff) = slope*diff + intercept with f(max_diff) = 10 and f(min_diff) = 0
        relative_scores_per_metric[metric] = {puuid: slope*differences[puuid_to_role[puuid]] + intercept for puuid in winners}
        relative_scores_per_metric[metric].update({puuid: 10 - (slope*differences[puuid_to_role[puuid]] + intercept) for puuid in losers})

    # Compute each player's score (defined as sum(metric_weight*metric_absolute_score for all metrics))
    absolute_scores = {puuid: sum({metric: configs.WEIGHTS[metric]*absolute_scores_per_metric[metric][puuid] for metric in metrics_to_puuid}.values()) for puuid in puuids} 
    relative_scores = {puuid: sum({metric: configs.WEIGHTS[metric]*relative_scores_per_metric[metric][puuid] for metric in metrics_to_puuid}.values()) for puuid in puuids} 
    scores = {puuid: configs.ABSOLUTE_WEIGHT*absolute_scores[puuid] + configs.RELATIVE_WEIGHT*relative_scores[puuid] for puuid in puuids}

    # Sort then round
    scores = {k: v for k, v in sorted(scores.items(), key = lambda item: item[1], reverse = True)} # Sort them by descending value
    scores = {key: round(value, 2) for (key, value) in scores.items()}    

    # This is a detailled summary
    if explained:
        scores_per_metrics = {metric: {puuid_to_champ_name[puuid]: {"value": metrics_to_puuid[metric][puuid], 
                                                                    "absolute score": absolute_scores_per_metric[metric][puuid],
                                                                    "relative score": relative_scores_per_metric[metric][puuid]
                                                                    } for puuid in puuids} for metric in configs.METRICS}



    return scores if not explained else scores_per_metrics
