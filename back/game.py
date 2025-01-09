import community_dragon as cdragon
import configs 
import riot_api
import utils
from models import *

import re

from functools import reduce
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from itertools import permutations


class Game():
    def __init__(self, game_data, summoner):

        # Game data
        self.game_data = game_data
        self.queue_id = str(self.game_data["gameQueueConfigId"])
        self.tft = self.queue_id in configs.TFT_QUEUE_IDS
        self.game_id = "{platform}_{game_id}".format(platform = self.game_data["platformId"], game_id = self.game_data["gameId"])
        self.participants = self.game_data["participants"]
        self.participant = [participant for participant in self.participants if participant.get("summonerId") == summoner.summoner_id][0] # summonerId is not a key in TFT spectator games but we don't need participant in this case
        #self.game_start_timer = utils.convert_epoch_to_datetime(self.game_data["gameStartTime"]/1000).strftime(configs.DMYHMS_FORMAT) # This take a few minutes to be updated by Riot - defaults to 1st Jan 1970

        # Summoner data
        self.summoner = summoner # We bind the summoner we are monitoring to the Game
        self.entry = self.summoner.get_entry(self.queue_id)


    @staticmethod
    def champion_image(champ_path, sum1_path, sum2_path):
        """Stacks the summoners icons at the right of the champion icon."""

        # Get the widths and heights of the images
        champ_icon = Image.open(BytesIO(cdragon.get_content_at_path(champ_path)))
        width, height = champ_icon.size

        # Set the digit to add
        digit = '1'

        # Set the font and font size
        font = ImageFont.truetype('arial.ttf', 40)

        # Create a new image for the circled digit
        digit_img = Image.new('RGBA', (50, 50), (255, 255, 255, 0))
        draw = ImageDraw.Draw(digit_img)

        # Draw a circle
        draw.ellipse((10, 10, 40, 40), fill=(255, 255, 255), outline=(0, 0, 0))

        # Calculate the text width and height
        # text_width, text_height = font.getsize(digit)
        text_width, text_height = digit_img.size
        # Calculate the x and y coordinates to center the text
        x = (50 - text_width) / 2
        y = (50 - text_height) / 2

        # Draw the digit
        draw.text((x, y), digit, font=font, fill=(0, 0, 0))
        # Paste the circled digit onto the original image
        champ_icon.paste(digit_img, (10, 10), digit_img)


        # Resize the summoners icons to match the size of the top champion icon
        sum_icons = [Image.open(BytesIO(cdragon.get_content_at_path(path))) for path in (sum1_path, sum2_path)]
        new_width = int(width/2) # Divide the widths by 2
        new_height = new_width
        sum_icons = [sum_icon.resize((new_width, new_height)) for sum_icon in sum_icons]

        # Create the new image
        new_img = Image.new('RGB', (width + new_width, height))
        new_img.paste(champ_icon, (0, 0)) # Paste the unit icon at the top of the new image
        offset = 0
        for sum_icon in sum_icons:
            new_img.paste(sum_icon, (width, offset)) # Paste the item icons underneath
            offset += new_height

        return new_img


    @staticmethod
    def stack_images(image1, image2):
        """Stacks two images horizontally."""

        # Get the widths and heights of the images
        w1, h1 = image1.size
        w2, h2 = image2.size
        if h1 != h2:
            # Resize the images to have the same height
            if h1 > h2:
                image2 = image2.resize((int(w2 * h1 / h2), h1))
            else:
                image1 = image1.resize((int(w1 * h2 / h1), h2))

        # Create a new image with the total width of the two images
        image = Image.new('RGB', (w1 + w2, h1))
        image.paste(image1, (0, 0))
        image.paste(image2, (w1, 0))

        return image


    # TODO: loss prevented
    @staticmethod
    def check_for_game_result(past_entry, new_entry):
        """Compares the two entries to spot end game results."""

        # Get the stats
        past_tier = past_entry["tier"].capitalize()
        past_division = past_entry["rank"]
        past_lp = past_entry["leaguePoints"] 
        past_wins = past_entry["wins"]
        past_losses = past_entry["losses"]
        past_games = past_wins + past_losses

        new_tier = new_entry["tier"].capitalize()
        new_division = new_entry["rank"]
        new_lp = new_entry["leaguePoints"]
        new_wins = new_entry["wins"]
        new_losses = new_entry["losses"]
        new_games = new_wins + new_losses
        new_rating = utils.format_entry(new_entry)

        # Check if the summoner was/is unranked
        was_unranked = past_tier.upper() == "UNRANKED"
        if was_unranked:
            past_progress = past_entry["placements"]["progress"]
        is_unranked = new_tier.upper() == "UNRANKED"
        if is_unranked:
            new_progress = new_entry["placements"]["progress"]
            formatted_new_progress = utils.format_progress(new_progress)

        # The result is a string "description"
        description = ""

        # If there has been a game played, get its result
        if new_games - past_games == 1:
            won = new_wins == past_wins + 1

            # Unranked games
            if was_unranked:
                if is_unranked:
                    if past_games == 0:
                        description = f"They won their first placement game ({formatted_new_progress})!" if won else f"They lost their first placement game ({formatted_new_progress})."
                    else:
                        description = f"They won a placement game ({formatted_new_progress})!" if won else f"They lost a placement game ({formatted_new_progress})."
                else:
                    progress = utils.update_progress(past_progress, won)
                    formatted_progress = utils.format_progress(progress)
                    description = f"They won their last placement game and placed {new_rating} ({formatted_progress})!" if won else f"They lost their last placement game and placed {new_rating} ({formatted_progress})."

            # Tier change (eg Gold IV to Silver I)
            elif past_tier != new_tier:
                description = f"They got promoted to {new_rating}!" if won else f"They got demoted to {new_rating}."

            # Promoted (with skips) or demoted from a division (eg Gold III to Gold IV)
            elif past_division != new_division:
                skip = utils.find_index(new_division, configs.RANKS) - utils.find_index(past_division, configs.RANKS)
                if skip >= 2:
                    description = f"They skipped a division and promoted to {new_rating}!"
                else:
                    lp_gain = utils.entry_to_number(new_entry) - utils.entry_to_number(past_entry)
                    description = f"They won {lp_gain} LP and got promoted to {new_rating}!" if won else f"They got demoted to {new_rating}."

            # Finally, if we get there it's a regular game
            else:
                description = f"They won {new_lp - past_lp} LP!" if won else f"They lost {past_lp - new_lp} LP."
                
        return description


    @staticmethod
    def infer_roles(champion_ids, pickrates, smite_holder = None):
        """Infer roles for the given 5 champions according to the pickrate data."""
        current_best_objective = 0 # Current best "objective" (sum of pickrates - product is too harsh)
        current_best_permutation = None # Current best permutation
        roles = set([role for dic in pickrates.values() for role in dic.keys()])
        
        # If we know that only one of the five champions has smite, we can safely assume they are the Jungler
        if smite_holder is not None:
            roles.remove("JUNGLE")
            champion_ids.remove(smite_holder)

        # Find the permutation that maximizes the sum of pickrates
        for permutation in permutations(champion_ids):
            ith_champion_id = 0
            current_objective = 0
            for role in roles:
                current_objective += pickrates[permutation[ith_champion_id]].get(role, 0) # permutation[i] is a champion_id so permutation[i][role] is the pickrate of that champion_id for this role
                ith_champion_id += 1
            if current_objective >= current_best_objective:
                current_best_objective = current_objective
                current_best_permutation = {champion_id: role for (role, champion_id) in zip(roles, permutation)}

        # Add back the Jungler
        if smite_holder is not None:
            current_best_permutation[smite_holder] = "JUNGLE"

        # Convert the default roles names (eg Utility to Support)
        current_best_permutation = {key: configs.POSITION_TO_ROLE[value] for (key, value) in current_best_permutation.items()}

        return current_best_permutation


    def in_game_message_log(self):
        """Creates the message displayed when a summoner gets in a game."""

        # Retrieve game information 
        self.sum1_data = cdragon.SUMMONER_SPELLS_ID_TO_PATH_AND_NAME[self.participant["spell1Id"]]
        self.sum2_data = cdragon.SUMMONER_SPELLS_ID_TO_PATH_AND_NAME[self.participant["spell2Id"]]
        self.champ_data = cdragon.CHAMPION_ID_TO_PATH_AND_NAME[self.participant["championId"]]
        self.team_id = self.participant["teamId"]

        # Infer the role played and the ennemy champion
        pickrates = cdragon.PICKRATES 
        ally_champion_ids = [participant["championId"] for participant in self.participants if participant["teamId"] == self.team_id]
        ally_smites = [participant["championId"] for participant in self.participants if participant["teamId"] == self.team_id and (participant["spell1Id"] == 11 or participant["spell2Id"] == 11)]
        infer_ally_map = self.infer_roles(ally_champion_ids, pickrates, smite_holder = ally_smites[0] if len(ally_smites) == 1 else None) # Map champ_id: inferred role
        ennemy_champion_ids = [participant["championId"] for participant in self.participants if participant["teamId"] != self.team_id]
        ennemy_smites = [participant["championId"] for participant in self.participants if participant["teamId"] != self.team_id and (participant["spell1Id"] == 11 or participant["spell2Id"] == 11)]
        infer_ennemy_map = self.infer_roles(ennemy_champion_ids, pickrates, smite_holder = ennemy_smites[0] if len(ennemy_smites) == 1 else None)
        inferred_role = infer_ally_map[self.participant["championId"]]
        inferred_ennemy_champ_id = {value: key for (key, value) in infer_ennemy_map.items()}[inferred_role]

        # Get opponent summoner spells and champion image
        for participant in self.participants:
            if participant["championId"] == inferred_ennemy_champ_id:
                ennemy_sum1_id = participant["spell1Id"]
                ennemy_sum2_id = participant["spell2Id"]
        ennemy_sum1_data = cdragon.SUMMONER_SPELLS_ID_TO_PATH_AND_NAME[ennemy_sum1_id]
        ennemy_sum2_data = cdragon.SUMMONER_SPELLS_ID_TO_PATH_AND_NAME[ennemy_sum2_id]
        inferred_ennemy_champ_data = cdragon.CHAMPION_ID_TO_PATH_AND_NAME[inferred_ennemy_champ_id]    

        # Check if there was any good ban (ie banning a champion on which one of the ennemy team has > 250k mastery points and has played in the last ten days)
        banned_champ_to_participant = {champ["championId"]: (0, None) for champ in self.game_data["bannedChampions"] if champ["teamId"] == self.team_id}
        for participant in self.participants:
            if participant["teamId"] != self.team_id:
                for champ_id in banned_champ_to_participant:
                    mastery = riot_api.get_champion_mastery(participant["summonerId"], champ_id)
                    if mastery is not None: # Can be None if the summoner has never played this champ
                        points = mastery["championPoints"]
                        last_played = utils.convert_epoch_to_datetime(mastery["lastPlayTime"]/1000)
                        days_since_last_played = (utils.now() - last_played).seconds//(3600*24)
                        if points > max(250000, banned_champ_to_participant[champ_id][0]) and days_since_last_played < 10:
                            banned_champ_to_participant[champ_id] = (points, participant)
        bans = ""
        for champ_id in banned_champ_to_participant:
            champ_name = cdragon.CHAMPION_ID_TO_PATH_AND_NAME[champ_id]["name"] # Handles None bans (cdragon returns None)
            bans += f"\n{champ_name}"
            mastery, ennemy = banned_champ_to_participant[champ_id]
            if mastery != 0:
                ennemy_champ =  cdragon.CHAMPION_ID_TO_PATH_AND_NAME[ennemy["championId"]]["name"]
                mastery_k = int(round(mastery/1000))
                bans += f" - good ban: ennemy {ennemy_champ} has {mastery_k:,}k mastery points on it"

        # Create the embed
        title =  f"{self.summoner.riot_name} just got into a game!"
        description = "They are playing {champ} {role} against {ennemy_champ}.".format(champ = self.champ_data["name"], role = inferred_role.capitalize(), ennemy_champ = inferred_ennemy_champ_data["name"])
        embed = {"title": title, "description": description, "color": configs.ORANGE}

        # The fields are current_rating | bans
        current_rating = utils.format_entry(self.entry)
        field_rating = {"name": "Rank", "value": current_rating, "inline": True}
        field_ban = {"name": "Bans", "value": bans, "inline": False}
        fields = [field_rating, field_ban]

        # The image is the champion's icon | the summoner spells vs inferred ennemy champion's icon | ennemy summoner spells
        image = self.champion_image(self.champ_data["path"], self.sum1_data["path"], self.sum2_data["path"])   
        ennemy_image = self.champion_image(inferred_ennemy_champ_data["path"], ennemy_sum1_data["path"], ennemy_sum2_data["path"])   
        image = self.stack_images(image, ennemy_image)

        # The footer is the timestamp
        ts = utils.now().strftime(configs.DMYHMS_FORMAT)

        # Create the message log
        message_log = {"embed": embed, "fields": fields, "image": image, "footer": ts, "done_with": False}

        return message_log

    def tft_in_game_database_entry(self):
        """Format the event to be inserted in the database when a summoner gets in a game."""

        # The fields are current_rating
        current_rating = utils.format_entry(self.entry)
        ts = utils.now().strftime(configs.DMYHMS_FORMAT)

        liveEvent: LiveEvent = LiveEvent(
            player = self.summoner.riot_name,
            rank = current_rating,
            status = 'entered',
            timestamp = ts
        )
        
        return liveEvent
    
    def tft_out_of_game_database_entry(self):
        """Format the event to be inserted in the database when a summoner get out of a game."""
        # cdragonAugments = [cdragon.TFT_MISC_ID_TO_PATH_AND_NAME[augment] for augment in self.participant["augments"]]        
        # augments = [Augment(name=augment.name, stars=augment.stars) for augment in cdragonAugments]
        augments = []

        placement = int(self.participant["placement"])
        game_length = int(self.participant["time_eliminated"]) # In seconds
        
        last_round = int(self.participant["last_round"])
        
        # Find the top1 comp
        winner = [participant for participant in self.participants if participant["placement"] == 1][0]
        # winner_units = self.sort_units(winner["units"])
        # winner_units = winner['units']
        # winner_traits = [trait for unit in winner_units for trait in unit["traits"]]
        # winner_traits = {trait: len([t for t in winner_traits if t == trait]) for trait in winner_traits}
        # best_traits = sorted(winner_traits, key = winner_traits.get, reverse = True)[:2] # Only keep the two most common traits

        new_rating = utils.format_entry(self.new_entry)
        
        ts = utils.now().strftime(configs.DMYHMS_FORMAT)

        gameInfo: GameInfo = GameInfo(
            rounds= last_round,
            result= "lose" if not winner["puuid"] == self.participant["puuid"] else "win",
            new_rating=new_rating,
            top_comp= "",
            placement=placement,
            duration=game_length,
            augments=augments
        )

        liveEvent: LiveEvent = LiveEvent(
            player = self.summoner.riot_name,
            rank = new_rating,
            status = 'exited',
            timestamp = ts,
            game_info=gameInfo
        )

        return liveEvent

    def tft_in_game_message_log(self):
        """Creates the message displayed when a summoner gets in a game."""
        
        # Create the embed
        title =  f"{self.summoner.riot_name} just got into a game!"
        embed = {"title": title, "color": configs.DARK_ORANGE}

        # The fields are current_rating
        current_rating = utils.format_entry(self.entry)
        field_rating = {"name": "Rank", "value": current_rating, "inline": True}
        fields = [field_rating]

        # The footer is the timestamp
        ts = utils.now().strftime(configs.DMYHMS_FORMAT)

        # Create the message log
        message_log = {"embed": embed, "fields": fields, "footer": ts, "done_with": False, "tft": True}

        return message_log
    
    # TODO: differentiate between remakes and early ffs < 15mn (if possible)
    # TODO: add both levels bottom right of images (source the lvl numbers from cdragon)
    def out_of_game_message_log(self):
        """Creates the message displayed when a summoner gets out of a game."""

        # Retrieve game statistics about our summoner
        game_length = self.game_data["gameDuration"] # In seconds
        remake = self.participant["gameEndedInEarlySurrender"] or (not self.participant["eligibleForProgression"]) # The eligibleForProgression can help spot remakes that are tagged with gameEndedInEarlySurrender = False (eg: game_id = EUW1_6801162354)
        metrics = utils.get_metrics(self.participant)
        win = metrics["win"] 
        kp = int(round(100*metrics["kill_participation"], 0))
        kills = metrics["kills"]
        deaths = metrics["deaths"]
        assists = metrics["assists"]
        vision_score = metrics["vision_score"]
        cs = metrics["cs"]
        cspm = round(60*cs/(game_length - 90), 1) # 1mn30 before minions spawn
        kda = f"{kills}/{deaths}/{assists}"
        kda_num = round((kills + assists)/deaths, 2) if deaths != 0 else 69420
        pings = sum([value for (key, value) in self.participant.items() if "ping" in key.lower()])
        pings_pm = round(60*pings/game_length, 1)
        total_team_dmg = sum([utils.get_metrics(participant)["damage_to_champions"] for participant in self.participants if participant["teamId"] == self.team_id])
        damage_share = int(round(100*metrics["damage_to_champions"]/total_team_dmg, 0)) if total_team_dmg != 0 else 0
                    
        # Retrieve role information about all participants and find the opponent
        puuid_to_role = utils.get_role_played(self.participants)
        played_role = puuid_to_role[self.summoner.puuid]
        found_ennemy = False
        for participant in self.participants:
            puuid = participant["puuid"]
            if puuid != self.summoner.puuid and puuid_to_role[puuid] == played_role:
                ennemy_sum1 = cdragon.SUMMONER_SPELLS_ID_TO_PATH_AND_NAME[participant["summoner1Id"]]
                ennemy_sum2 = cdragon.SUMMONER_SPELLS_ID_TO_PATH_AND_NAME[participant["summoner2Id"]]
                ennemy_champ = cdragon.CHAMPION_ID_TO_PATH_AND_NAME[participant["championId"]]
                found_ennemy = True

        # Compute scores and find mvp/ace
        if not remake and ("Unknown" not in utils.get_role_played(self.participants).values()):
            scores = utils.compute_score(self.game_data)
            scores_str = ""
            for counter, puuid in enumerate(scores):
                score = scores[puuid]
                participant = [participant for participant in self.participants if participant["puuid"] == puuid][0]
                participant_champ = cdragon.CHAMPION_ID_TO_PATH_AND_NAME[participant["championId"]]["name"]
                participant_metrics =  utils.get_metrics(participant)
                participant_kda = "{}/{}/{}".format(participant_metrics["kills"], participant_metrics["deaths"], participant_metrics["assists"])
                pm = "+" if participant["win"] == win else "-"
                scores_str += f"\n{pm}{counter + 1}) {participant_champ} ({participant_kda}): {score}" # counter + 1 because counter starts at 0
            scores_str = f"""```diff\n{scores_str}```\n""" # diff to have red/green formatting
            mvp_role = puuid_to_role[max({participant["puuid"]: scores[participant["puuid"]] for participant in self.participants if participant["win"]}.items(), key = lambda item: item[1])[0]]
            ace_role = puuid_to_role[max({participant["puuid"]: scores[participant["puuid"]] for participant in self.participants if not participant["win"]}.items(), key = lambda item: item[1])[0]]

        # Create the embed
        title =  f"{self.summoner.riot_name} just got out of a {utils.convert_seconds_to_hms(game_length)} game on {{champ}} {played_role}!".format(champ = self.champ_data["name"])
        description = self.check_for_game_result(self.entry, self.new_entry)
        if remake:
            remake_because_of_them = (self.new_entry["losses"] == self.entry["losses"] + 1)
            if remake_because_of_them:
                description = f"{description}\nThe game was remade because of them." # If the game has been remade because of them, they will have one more loss
            else:
                description = "The game was remade." # Otherwise, their number of games stay the same and check_for_game_result will return an empty string # TODO: check
        else:
            diff = f"The game was a {mvp_role} difference."
            description = f"{description}\n{diff}"
        colour = configs.BLACK if remake else (configs.GREEN if win else configs.RED) 
        embed = {"title": title, "description": description, "color": colour}   

        # The fields are new_rating | kda & kp | cs/min & vision score | pings | damage share | scores
        new_rating = utils.format_entry(self.new_entry)
        field_rating = {"name": "Rank", "value": new_rating, "inline": True}
        field_kda_kp = {"name": "KDA & KP", "value": f"{kda} ({kda_num}) & {kp}%", "inline": True}
        field_csm_and_vision_score = {"name": "CS & vision score", "value": f"{cs} ({cspm}) & {vision_score}", "inline": True}
        field_pings = {"name": "Pings", "value": f"{pings} ({pings_pm})", "inline": True}
        field_damage_share = {"name": "Damage share", "value": f"{damage_share}%", "inline": True}
        fields = [field_rating, field_kda_kp, field_csm_and_vision_score, field_pings, field_damage_share]     
        if not remake:
            field_scores = {"name": f"Scores (game id: {self.game_id})", "value": scores_str, "inline": False}
            fields.append(field_scores)   

        # The image is the champion's icon | the summoner spells vs ennemy champion's icon | ennemy summoner spells
        image1 = self.champion_image(self.champ_data["path"], self.sum1_data["path"], self.sum2_data["path"]) 
        if found_ennemy:
            image2 = self.champion_image(ennemy_champ["path"], ennemy_sum1["path"], ennemy_sum2["path"])
        else:
            image2 = Image.open(BytesIO(cdragon.MISSING_PING))
        image = self.stack_images(image1, image2)    
        
        # The footer is the timestamp
        ts = utils.now().strftime(configs.DMYHMS_FORMAT)

        # The reactions are MVP/ACE if appropriate
        reactions = []
        if not remake:
            if win and mvp_role == played_role:
                reactions = [configs.REGIONAL_INDICATOR_M, configs.REGIONAL_INDICATOR_V, configs.REGIONAL_INDICATOR_P]
            elif (not win) and ace_role == played_role:
                reactions = [configs.REGIONAL_INDICATOR_A, configs.REGIONAL_INDICATOR_C, configs.REGIONAL_INDICATOR_E]    

        # Create the message log
        message_log = {"embed": embed, "fields": fields, "image": image, "footer": ts, "reactions": reactions, "done_with": False}
        
        return message_log


    @staticmethod
    def unit_image(unit_path, item_pathes, stars):
        """Stacks the items icons (if any) underneath the unit icon."""

        # Add the stars to the unit_icon
        star = Image.open(BytesIO(cdragon.TFT_STAR))
        star = star.resize((int(1.75*star.width), int(1.75*star.height)))
        unit_icon = Image.open(BytesIO(cdragon.get_content_at_path(unit_path, tft = True)))
        width, height = unit_icon.size
        offsets = {1: [(width - star.width, 0)], 
                   2: [(width - star.width, 0), (width - 2*star.width, 0)],
                   3: [(width - star.width, 0), (width - 2*star.width, 0), (int(width - 1.5*star.width), int(0.1*height))]
                   }[stars]
        for offset in offsets:  
            unit_icon.paste(star, (offset[0], offset[1]))

        # Resize the item icons to match the size of the top unit icon
        item_icons = [Image.open(BytesIO(cdragon.get_content_at_path(item_path, tft = True))) for item_path in item_pathes]
        new_width = int(width/3) # Divide the widths by 2 and then by 3 (#items max)
        new_height = new_width    
        item_icons = [item_icon.resize((new_width, new_height)) for item_icon in item_icons]

        # Create the new image
        new_img = Image.new('RGB', (width, height + new_height), color = "#2B2D31") # This is Discord's font (to align itemless spaces)
        new_img.paste(unit_icon, (0, 0)) # Paste the unit icon at the top of the new image
        # offsets = {3: [0, int((width - new_width)/2), width - new_width],
        #            2: [int((width - new_width)/4), 3*int((width - new_width)/4)],
        #            1: [int((width - new_width)/2)],
        #            0: [0]}[len(item_icons)]
        offsets = [0, int((width - new_width)/2), width - new_width]
        for item_icon, offset in zip(item_icons, offsets):
            new_img.paste(item_icon, (offset, height)) # Paste the item icons underneath
        return new_img


    @staticmethod
    def sort_units(units):
        """Sorts the units by traits, stars and number of items."""
        traits = {}
        for unit in units:
            unit.update(cdragon.TFT_CHAMPIONS_ID_TO_PATH_AND_NAME[unit["character_id"]])
            unit["items"] = [cdragon.TFT_MISC_ID_TO_PATH_AND_NAME[item] for item in unit["itemNames"]]
            for trait in unit["traits"]:
                traits[trait] = traits.get(trait, 0) + 1
        ordered_traits = {trait: sorted(traits, key = traits.get).index(trait) for trait in traits} # Avoid ties
        sort_trait = lambda traits: max([ordered_traits[trait] for trait in traits]) if traits else -1 # Yuumi has no traits
        sort = lambda unit: (sort_trait(unit["traits"]), unit["tier"], len(unit["items"]))
        res = sorted(units, reverse = True, key = sort)
        return res

    
    @staticmethod
    def get_augment_tier(augment):
        """Gets the augment tier (1 for silver, 2 for gold, 3 for prismatic.)"""
        path = augment["path"]
        capture = re.search(configs.TFT_REGEX, path.split("/")[-1])
        if capture:
            res = max(len([c for c in re.search(configs.TFT_REGEX, path.split("/")[-1]).group() if c.lower() == "i"]), 1) # Default to 1
        else:
            res = 1 if "1" in path else (2 if "2" in path else (3 if "3" in path else 10))
        return res


    def tft_out_of_game_message_log(self):
        """Creates the message displayed when a summoner gets out of a game."""

        # Retrieve game statistics about our summoner
        game_length = int(self.participant["time_eliminated"]) # In seconds
        placement = self.participant["placement"]
        augments = [cdragon.TFT_MISC_ID_TO_PATH_AND_NAME[augment] for augment in self.participant["augments"]]
        augments = "\n".join(["{name} ({stars})".format(name = augment["name"], stars = configs.STARS*self.get_augment_tier(augment)) for augment in augments])
        last_round = self.participant["last_round"]
        level = self.participant["level"]
        units = self.participant["units"]

        # Find the top1 comp
        winner = [participant for participant in self.participants if participant["placement"] == 1][0]
        winner_units = self.sort_units(winner["units"])
        winner_traits = [trait for unit in winner_units for trait in unit["traits"]]
        winner_traits = {trait: len([t for t in winner_traits if t == trait]) for trait in winner_traits}
        best_traits = sorted(winner_traits, key = winner_traits.get, reverse = True)[:2] # Only keep the two most common traits

        # Create the embed
        title =  f"{self.summoner.riot_name} just got out of a {last_round} rounds and {utils.convert_seconds_to_hms(game_length)} game!"
        description = self.check_for_game_result(self.entry, self.new_entry)
        if not winner["puuid"] == self.participant["puuid"]:
            description = f"{description}\n The top comp was {best_traits[0]} {winner_traits[best_traits[0]]} & {best_traits[1]} {winner_traits[best_traits[1]]}."
        colour = configs.GREEN if placement <= 4 else configs.RED
        embed = {"title": title, "description": description, "color": colour}   

        # The fields are new_rating | placement | augments
        new_rating = utils.format_entry(self.new_entry)
        field_rating = {"name": "Rank", "value": new_rating, "inline": True}
        field_placement = {"name": "Placement", "value": placement, "inline": True}
        field_augments = {"name": "Augments", "value": augments, "inline": True}
        fields = [field_rating, field_placement, field_augments]

        # The image is the units played (with items)
        units = self.sort_units(units)
        stack = lambda img1, img2: self.stack_images(img1, img2)
        images = [self.unit_image(unit["path"], [item["path"] for item in unit["items"]], unit["tier"]) for unit in units]
        image = reduce(stack, images)

        # The footer is the timestamp
        ts = utils.now().strftime(configs.DMYHMS_FORMAT)

        # The reaction is "TOP{placement}"
        reaction_placement = configs.DIGITS[placement - 1]
        reactions = [configs.REGIONAL_INDICATOR_T, configs.REGIONAL_INDICATOR_O, configs.REGIONAL_INDICATOR_P, reaction_placement]    

        # Create the message log
        message_log = {"embed": embed, "fields": fields, "image": image, "reactions": reactions, "footer": ts, "done_with": False, "tft": True}
        
        return message_log


    def has_ended(self):
        """Returns True if the game has ended and gathers the end game data."""
        game_data = riot_api.get_ended_game_info(self.game_id, tft = self.tft)
        if game_data is not None:
            self.game_data = game_data["info"]
            self.participants = self.game_data["participants"]
            self.participant = [participant for participant in self.participants if (participant.get("summonerId") == self.summoner.summoner_id) or (participant.get("puuid") == self.summoner.puuid)][0] # TFT games use puuid
            self.new_entry = self.summoner.get_entry(self.queue_id)
            return True
        return False
        