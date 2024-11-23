def create_about_to_decay_alert(entry, last_game_timestamp):
    """Creates the message displayed when a summoner is about to decay - rules from https://support-leagueoflegends.riotgames.com/hc/en-us/articles/4405783687443."""

    # Find the new rating (if the summoner were to drop at or below 0 LP, they would be placed in the previous division at 75 LP - even for master despite what the link above says)
    lp_loss = configs.DECAY_LP.get(entry["tier"].upper(), 0)
    current_lp = entry["leaguePoints"]
    if current_lp - lp_loss <= 0:
        if entry["tier"].upper() in configs.APEX_TIERS:
            next_rating = "Diamond I 75 LP"  # Not D2 despite what the link says
        else:
            next_rating = utils.format_entry(
                utils.get_adjacent_entry(entry, get_next=False)
            )
    else:
        current_rating_number = utils.entry_to_number(entry)
        next_rating = utils.format_entry(
            utils.number_to_entry(current_rating_number - lp_loss)
        )  # Apex tiers will be defaulted to the lowest one

    # Find the (tentative) decay timestamp - this only works if they stopped playing with the maximum amount of days banked
    decay_days = configs.DECAY_DAYS.get(entry["tier"].upper(), 0)
    decay_ts = (
        (last_game_timestamp + datetime.timedelta(days=decay_days))
        .astimezone(pytz.timezone(configs.TIMEZONE))
        .strftime(configs.DMYHMS_FORMAT)
    )
