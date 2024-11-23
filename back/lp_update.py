import configs
import summoner as Summ
import utils

import json


def create_lp_update(queue_id = "420"):
    """Creates the message displayed in the summary Discord channel."""

    # Load the puuids
    with open(configs.PUUID_PATH, encoding = "utf-8") as json_data:
        data = json.load(json_data)   
        puuids = list(data.keys())

    # Load the last summary and update its timestamp
    with open(configs.LP_UPDATE_PATH, encoding = "utf-8") as json_data:
        summary = json.load(json_data)
        present_puuids = [puuid for puuid in summary.keys() if puuid not in ["timestamp", "timezone"]]
        all_puuids = list(set(puuids + present_puuids))
    past_ts = summary.get("timestamp", None)
    past_timezone = summary.get("timezone", configs.TIMEZONE)
    past_ts_dt = utils.string_to_datetime(ts = past_ts, timezone = past_timezone)
    new_ts_dt = utils.now()
    summary["timestamp"] = new_ts_dt.strftime(configs.DMYHMS_FORMAT)
    summary["timezone"] = configs.TIMEZONE

    # Create the embed
    hours = (new_ts_dt - past_ts_dt).days*24 + int(round((new_ts_dt - past_ts_dt).seconds/3600))
    title = "Summary over the weekend" if new_ts_dt.weekday() == 0 else ("Summary over the day" if hours <= 30 else 
                                                                       "Summary since {last}".format(last = past_ts_dt.strftime(configs.DMYHMS_FORMAT)))
    embed = {"title": title, "color": configs.AQUA}    
    fields = []

    # Find the summary for each puuid
    for puuid in all_puuids:
        past = summary.get(puuid, {})

        # Load the corresponding summoner
        summoner = Summ.Summoner(puuid = puuid)
        entry = summoner.get_entry(queue_id)

        # LP difference
        new_rating_number = utils.entry_to_number(entry)
        past_rating_number = past.get("rating_number", 0)
        lp_diff = new_rating_number - past_rating_number
        pm = "+" if lp_diff >= 0 else "-"
        
        # Number of games
        new_wins = entry["wins"] 
        new_losses = entry["losses"]
        new_total = new_wins + new_losses
        past_wins = past.get("wins", new_wins)
        past_losses = past.get("losses", new_losses)
        past_total = past_wins + past_losses
        number_of_wins = new_wins - past_wins
        number_of_losses = new_losses - past_losses
        number_of_games = new_total - past_total

        # Number of dodges (if any)
        number_of_dodges = past.get("dodges", 0)

        # Ratings
        new_rating = utils.format_entry(entry)
        past_rating = past.get("rating", new_rating)

        # Find out if there is any difference
        diff = (number_of_wins != 0) or (number_of_losses != 0) or (new_rating != past_rating) or (number_of_dodges != 0)

        # Update the summary (and reset the dodge counter)
        summary[puuid] = {"rating_number": new_rating_number, "wins": new_wins, "losses": new_losses, "rating": new_rating}

        # If there is a difference, print it to Discord
        games = "games" if number_of_games > 1 else "game"
        wins = "wins" if number_of_wins > 1 else "win"
        losses = "losses" if number_of_losses > 1 else "loss"
        dodges = "dodges" if number_of_dodges > 1 else "dodge"
        if diff and puuid in puuids:
            summary_formatted = f"{past_rating} to {new_rating}: {number_of_games} {games} ({number_of_wins} {wins} - {number_of_losses} {losses} - {number_of_dodges} {dodges})"
            field = {"name": f"{summoner.riot_name}: {pm}{abs(lp_diff)}", "value": summary_formatted, "inline": False, "diff": lp_diff}
            fields.append(field)

    # Save the new summary
    with open(configs.LP_UPDATE_PATH, "w", encoding = "utf-8") as json_data:
        json.dump(summary, json_data)

    # If there is no changement
    if len(fields) == 0:
        embed["description"] = f"No changes since {past_ts}"

    # Order the fields (in descending order)
    fields.sort(key = lambda field: abs(field["diff"]), reverse = True)

    # Create the message log
    message_log = {"embed": embed, "fields": fields, "footer": new_ts_dt.strftime(configs.DMYHMS_FORMAT), "done_with": False}
    return message_log        