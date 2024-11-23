import configs

class Change():
    def __init__(self, summoner, queue_ids):
        self.summoner = summoner
        self.queue_ids = queue_ids
        # self.entries = {queue_id: self.summoner.get_entry(queue_id) for queue_id in queue_ids}
        # TODO : voir si ça permet d'éviter les doublons au lancement du bot
        self.entries = {}


    def check_for_change(self):
        """Compares the new entry to spot decay, dodge, or drop from grandmaster/challenger due to cutoff moving (https://support-leagueoflegends.riotgames.com/hc/en-us/articles/4405783687443)."""
        res = {queue_id: None for queue_id in self.queue_ids}
        for (queue_id, entry) in self.entries.items():
            
            # Get the past stats
            past_tier = entry["tier"].capitalize()
            past_division = entry["rank"].capitalize()
            past_lp = entry["leaguePoints"] 
            past_games = entry["wins"] + entry["losses"]
            was_gm_chall = past_tier.upper() in configs.APEX_TIERS[1:]

            # Get the new stats
            new_entry = self.summoner.get_entry(queue_id)
            new_tier = new_entry["tier"].capitalize()
            new_division = new_entry["rank"].capitalize()
            new_lp = new_entry["leaguePoints"]
            new_games = new_entry["wins"] + new_entry["losses"]
            self.entries[queue_id] = new_entry # Update the entry

            # If there is a difference, it can only be decay/dodge (it could also be a remake but this is already handled in alerts.py's got_out_of_game)
            difference = ((past_tier != new_tier) or (past_division != new_division) or (past_lp != new_lp)) and (past_games == new_games) # TODO: check the impact a remake has on new_games (two cases: caused by the summoner or not)
            if difference:
                # If there is a tier/division drop or if the lp loss is greater than a threshold, it must be decay (lp loss from decay will carry over to the next tier/division)
                if (past_tier != new_tier) or (past_division != new_division) or (new_lp <= past_lp - min(configs.DECAY_LP.values())): 
                    res[queue_id] = "DECAY"

                # If there is an apex tier drop but the lp stayed the same, it means they are now below the cutoff
                elif was_gm_chall and past_tier != new_tier and new_lp == past_lp:
                    res[queue_id] = "GM_CHALL_DROP"

                # Otherwise, it has to be a dodge
                else:
                    # If the leaguePoints < 0 it means that this is an entry built by ourselves - we can't spot any further dodges in that case
                    if entry["leaguePoints"] >= 0:
                        res[queue_id] = "DODGE"
        return res
