import configs 
import riot_api
import utils

import datetime
import pytz




def create_about_to_decay_alert(entry, last_game_timestamp):
    """Creates the message displayed when a summoner is about to decay - rules from https://support-leagueoflegends.riotgames.com/hc/en-us/articles/4405783687443."""
  
    # Find the new rating (if the summoner were to drop at or below 0 LP, they would be placed in the previous division at 75 LP - even for master despite what the link above says)
    lp_loss = configs.DECAY_LP.get(entry["tier"].upper(), 0)
    current_lp = entry["leaguePoints"] 
    if current_lp - lp_loss <= 0:
        if entry["tier"].upper() in configs.APEX_TIERS:
            next_rating = "Diamond I 75 LP" # Not D2 despite what the link says
        else:
            next_rating = utils.format_entry(utils.get_adjacent_entry(entry, get_next = False))
    else:
        current_rating_number = utils.entry_to_number(entry)
        next_rating = utils.format_entry(utils.number_to_entry(current_rating_number - lp_loss)) # Apex tiers will be defaulted to the lowest one

    # Find the (tentative) decay timestamp - this only works if they stopped playing with the maximum amount of days banked
    decay_days = configs.DECAY_DAYS.get(entry["tier"].upper(), 0)
    decay_ts = (last_game_timestamp + datetime.timedelta(days = decay_days)).astimezone(pytz.timezone(configs.TIMEZONE)).strftime(configs.DMYHMS_FORMAT)

    # Create the embed
    game_name = entry["riotIdGameName"]
    tagline = entry["riotIdTagline"]
    title = f"{game_name}#{tagline} is about to decay!"
    description = f"They will decay to {next_rating}."
    embed = {"title": title, "description": description, "color": configs.DARK_RED}    

    # The fields are current_rating | lp_loss | decay timestamp
    current_rating = utils.format_entry(entry)
    field_rating = {"name": "Rank", "value": current_rating, "inline": True}
    field_lp_loss = {"name": "LP loss", "value": lp_loss, "inline": True}
    field_decay_ts = {"name": "Decay timestamp (tentative)", "value": decay_ts, "inline": True}
    fields = [field_rating, field_lp_loss, field_decay_ts]

    # The footer is the timestamp
    ts = utils.now().strftime(configs.DMYHMS_FORMAT)

    # Create the message log
    message_log = {"embed": embed, "fields": fields, "footer": ts, "done_with": False}
    return message_log        


def create_decayed_alert(past_entry, new_entry):
    """Creates the message displayed when a summoner decayed - rules from https://support-leagueoflegends.riotgames.com/hc/en-us/articles/4405783687443."""

    # Find the lp_loss
    past_rating_number = utils.entry_to_number(past_entry)
    new_rating_number = utils.entry_to_number(new_entry)
    lp_loss = past_rating_number - new_rating_number # Want this to be positive

    # Create the embed
    game_name = new_entry["riotIdGameName"]
    tagline = new_entry["riotIdTagline"]
    title = f"{game_name}#{tagline} decayed!"
    description = f"They lost {lp_loss} LP."
    embed = {"title": title, "description": description, "color": configs.DARK_RED}    

    # The fields are new_rating | lp_loss
    new_rating = utils.format_entry(new_entry)
    field_rating = {"name": "Rank", "value": new_rating, "inline": True}
    field_lp_loss = {"name": "LP loss", "value": lp_loss, "inline": True}
    fields = [field_rating, field_lp_loss]

    # The footer is the timestamp
    ts = utils.now().strftime(configs.DMYHMS_FORMAT)

    # Create the message log
    message_log = {"embed": embed, "fields": fields, "footer": ts, "done_with": False}
    return message_log        
 

def create_gm_chall_drop_alert(entry):
    """Creates the message displayed when a summoner drops from Grandmaster/Challenger (due to falling below the cutoff)."""

    # Get the new cutoff
    apex_tier = configs.APEX_TIERS[utils.find_index(entry["tier"].upper(), configs.APEX_TIERS) + 1]
    queue_id = configs.QUEUE_TYPE_TO_ID.get(entry["queueType"])
    cutoff, _ = riot_api.get_cutoff(apex_tier, queue_id)

    # Create the embed
    game_name = entry["riotIdGameName"]
    tagline = entry["riotIdTagline"]
    apex_tier = entry["tier"].capitalize()
    rating = utils.format_entry(entry)     
    title = f"{game_name}#{tagline} just dropped from apex tier {apex_tier}!"
    description = "They fell below the cutoff."
    embed = {"title": title, "description": description, "color": configs.PURPLE}

    # The fields are rating | new cutoff
    field_rating = {"name": "Rank", "value": rating, "inline": True}  
    field_cutoff = {"name": "Cutoff", "value": cutoff, "inline": True}
    fields = [field_rating, field_cutoff]

    # The footer is the timestamp
    ts = utils.now().strftime(configs.DMYHMS_FORMAT)

    # Create the message log
    message_log = {"embed": embed, "fields": fields, "footer": ts, "done_with": False}

    return message_log        
