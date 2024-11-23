import configs 
import utils

import datetime



class Dodge():
    def __init__(self, summoner):
        self.dodges = []
        self.summoner = summoner


    def add_a_dodge(self, ts):
        """Adds a dodge timestamp to the end of the list."""
        self.dodges.append(ts)

    
    def refresh_dodge_list(self):
        """Flushes out old dodges."""
        self.dodges = [ts for ts in self.dodges if (utils.now() - ts).seconds <= configs.DODGE_TIER_DROP]


    def dodge_message_log(self, entry_before_dodging):
        """Creates the message displayed when a summoner dodges a game - see https://support-leagueoflegends.riotgames.com/hc/en-us/articles/201751844-Queue-Dodging."""

        # Get the timestamp at which they can requeue next
        last_dodge = self.dodges[-1] # The last dodge (as in the dodge that happened the latest) will have been added last
        dodge = {1: configs.FIRST_DODGE, 2: configs.SECOND_DODGE, 3: configs.THIRD_DODGE}[len(self.dodges)]
        can_requeue_at = last_dodge + datetime.timedelta(seconds = dodge["timeout"])
        nth_time = {1: "first time", 2: "second time in a row", 3: "third time in a row"}[len(self.dodges)]

        # Get the time at which they drop a dodge tier
        first_dodge = self.dodges[0] # The first dodge (as in the dodge that happened the earliest) will have been added first
        time_to_drop_a_tier = first_dodge + datetime.timedelta(seconds = configs.DODGE_TIER_DROP) # This function is only ever called if there was a dodge - the list will never be empty here

        # Create the embed
        title = f"{self.summoner.riot_name} just dodged for the {nth_time}!"
        description = f"They can requeue on {can_requeue_at.strftime(configs.DMYHMS_FORMAT)}."
        embed = {"title": title, "description": description, "color": configs.LIGHT_GREY}

        # Update the entry and get the new_rating: substract the lp_loss (this goes into the negatives)
        entry_before_dodging["leaguePoints"] -= dodge["lp_loss"] # They dodged a game and lost lp - update lp (can be negative)
        new_rating = utils.format_entry(entry_before_dodging) 

        # The fields are new_rating | promo_loss or lp_loss | time needed to go down a tier
        field_rating = {"name": "Rank", "value": new_rating, "inline": True}  
        field_loss = {"name": "LP loss", "value": dodge["lp_loss"], "inline": True}
        field_time_to_drop_a_tier = {"name": "Next dodge tier drop", "value": f"{time_to_drop_a_tier.strftime(configs.DMYHMS_FORMAT)}", "inline": True}
        fields = [field_rating, field_loss, field_time_to_drop_a_tier]

        # The footer is the timestamp
        ts = utils.now().strftime(configs.DMYHMS_FORMAT)

        # The reactions are XD
        reactions = [configs.REGIONAL_INDICATOR_X, configs.REGIONAL_INDICATOR_D]    

        # Create the message log
        message_log = {"embed": embed, "fields": fields, "footer": ts, "reactions": reactions, "done_with": False}

        return message_log


