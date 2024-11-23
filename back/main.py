import configs
import lp_update
import riot_api
import utils

from mamie_bot import mamieBot
from summoner import Summoner

import datetime
import discord
import json
import pytz
import json
import traceback

from discord.ext import tasks, commands
from io import BytesIO


class MyClient(commands.Bot):
    def __init__(self, intents = discord.Intents.default(), command_prefix = configs.COMMAND_PREFIX):
        super().__init__(intents = intents, command_prefix = command_prefix)
        self.mamie_bot = mamieBot() # Setup mamie bot


        # Commands
        @self.command()
        async def add(context, *riot_id):
            """Adds the summoners (by game name + tagline) to the local puuid list - invoked by typing command_prefix add."""

            # First, get the summoners
            riot_id = " ".join(riot_id) # Put it back together
            riot_ids = riot_id.split(",")
            riot_ids = [riot_id.strip() for riot_id in riot_ids] # Remove leading and trailing whitespaces (introduced by a space after the comma in a command)
            summoners = [Summoner(riot_id = {"game_name": riot_id.split("#")[0], "tagline": riot_id.split("#")[1]}) for riot_id in riot_ids]

            # Then, add them to the list (if not already there)
            description = ""
            with open(configs.PUUID_PATH, encoding = "utf-8") as json_data:
                puuids = json.load(json_data)
            for summoner in summoners:
                if summoner.puuid in puuids:
                    description += f"\n{summoner.riot_name} was already there!"
                elif summoner.puuid is not None: # Will be None if there was no matching summoner for the given name/puuid
                    puuids[summoner.puuid] = summoner.riot_name
                    description += f"\n{summoner.riot_name} was added!"

            # Update the list
            with open(configs.PUUID_PATH, "w", encoding = "utf-8") as json_data:
                json.dump(puuids, json_data)        

            # Create the embed
            embed = {"title": "Summoner addition", "description": description, "color": configs.DARK_BLUE}
            embed = discord.Embed.from_dict(embed)
            ts = utils.now().strftime(configs.DMYHMS_FORMAT)   
            embed.set_footer(text = ts)                   
            await context.channel.send(embed = embed)


        @self.command()
        async def remove(context, *riot_id):
            """Removes the summoners (given the summoner names) from the local puuid list - invoked by typing command_prefix remove."""

            # First, get the summoner
            riot_id = " ".join(riot_id) # Put it back together
            riot_ids = riot_id.split(",")
            riot_ids = [riot_id.strip() for riot_id in riot_ids] # Remove leading and trailing whitespaces (introduced by a space after the comma in a command)
            summoners = [Summoner(riot_id = {"game_name": riot_id.split("#")[0], "tagline": riot_id.split("#")[1]}) for riot_id in riot_ids]

            # Then, remove it from the list (if it's in there)
            description = ""
            with open(configs.PUUID_PATH, encoding = "utf-8") as json_data:
                puuids = json.load(json_data)
            for summoner in summoners:
                if summoner.puuid in puuids:
                    del puuids[summoner.puuid]
                    description += f"\n{summoner.riot_name} was deleted!"
                elif summoner.puuid is not None: # Will be None if there was no matching summoner for the given name/puuid
                    description += f"\n{summoner.riot_name} wasn't here!"
        
            # Update the list
            with open(configs.PUUID_PATH, "w", encoding = "utf-8") as json_data:
                json.dump(puuids, json_data)                           

            # Create the embed
            embed = {"title": "Summoner deletion", "description": description, "color": configs.DARK_BLUE}
            embed = discord.Embed.from_dict(embed)
            ts = utils.now().strftime(configs.DMYHMS_FORMAT)   
            embed.set_footer(text = ts)                   
            await context.channel.send(embed = embed)                          


        @self.command()
        async def explain_scores(context, game_id):
            """Gives a detailled table of the scores for the given game_id."""

            # Load the tab
            current_game = riot_api.get_ended_game_info(game_id)
            game_info = current_game["info"]
            scores_per_metrics = utils.compute_score(game_info, explained = True)

            # Create the embed
            embed = {"title": f"Scores for game {game_id}",  "color": configs.DARK_BLUE}
            embed = discord.Embed.from_dict(embed)
            ts = utils.now().strftime(configs.DMYHMS_FORMAT)   
            embed.set_footer(text = ts)

            # Each field is a metric
            for metric in scores_per_metrics:
                scores_per_champ_name = scores_per_metrics[metric]
                sorted_scores = sorted(scores_per_champ_name, key = lambda key: scores_per_metrics[metric][key]["value"], reverse = True)
                description = ""
                for champ_name in sorted_scores:
                    value = scores_per_champ_name[champ_name]["value"]
                    absolute_score = scores_per_champ_name[champ_name]["absolute score"]
                    relative_score = scores_per_champ_name[champ_name]["relative score"]
                    description += f"\n {champ_name}: {round(value, 2)} ({round(absolute_score, 2)}, {round(relative_score, 2)})"
                embed.add_field(name = f"{metric} (coeff: {round(configs.WEIGHTS[metric], 2)})", value = description, inline = True)

            # Send the embed
            await context.channel.send(embed = embed)                        


        @self.command()
        async def cutoff(context, apex_tier, queue_id = "420"):
            """Gives the LP cutoff for the given apex_tier."""

            # Get the cutoff
            cutoff, summoner_id = riot_api.get_cutoff(apex_tier, queue_id)
            summoner = Summoner(summoner_id = summoner_id)
            summoner = Summoner(puuid = summoner.puuid) # Summoner by summoner_id doesn't give the game_name and tagline (but the API sends back summoner_id)
            description = f"The cutoff is {cutoff} (summoner: {summoner.riot_name})!"

            # Create the embed
            apex_tier = "Grandmaster" if apex_tier.upper() in ["GM", "GRANDMASTER"] else "Challenger"
            embed = {"title": f"Cutoff for apex tier {apex_tier}",  "color": configs.DARK_BLUE, "description": description}
            embed = discord.Embed.from_dict(embed)
            ts = utils.now().strftime(configs.DMYHMS_FORMAT)   
            embed.set_footer(text = ts)

            # Send the embed
            await context.channel.send(embed = embed)           


        @self.command()
        async def elo(context, *riot_id, queue_id = "420"):
            """Gives the elo of the given riot_id (if None, gives all registered summoners' elo)."""

            # If a riot_id is provided, fetch its rank
            if riot_id:
                riot_id = "".join(riot_id) # Put it back together
                riot_id = {"game_name": riot_id.split("#")[0], "tagline": riot_id.split("#")[1]}
                summoner = Summoner(riot_id = riot_id)
                entry = summoner.get_entry(queue_id)
                rating = utils.format_entry(entry)
                wins = entry["wins"]
                losses = entry["losses"]
                if "placements" in entry:
                    description = f"{summoner.riot_name} is currently {rating}!"
                else:
                    if entry["tier"] in configs.APEX_TIERS:
                        master = riot_api.get_apex_league(queue_id, "MASTER")["entries"]
                        grandmaster = riot_api.get_apex_league(queue_id, "GRANDMASTER")["entries"]
                        challenger = riot_api.get_apex_league(queue_id, "CHALLENGER")["entries"]
                        together = sorted(master + grandmaster + challenger, key = lambda participant: participant["leaguePoints"], reverse = True)
                        rank = 1
                        for participant in together:
                            if participant["summonerId"] == summoner.summoner_id:
                                break
                            else:
                                rank += 1
                        description = f"{summoner.riot_name} is currently {rating} (**{wins}/{losses}**) - rank **{rank}/{len(together)}**!"
                    else:
                        description = f"{summoner.riot_name} is currently {rating} (**{wins}/{losses}**)!"

            # Otherwise, fetch the registered summoners
            else:
                with open(configs.PUUID_PATH, encoding = "utf-8") as json_data:
                    puuids = json.load(json_data)
                everything = []
                for puuid in puuids:
                    summoner = Summoner(puuid = puuid)
                    entry = summoner.get_entry(queue_id)
                    everything.append((summoner.riot_name, entry))
                everything = sorted(everything, key = lambda x: utils.entry_to_number(x[1]), reverse = True)
                description = ""
                for name, entry in everything:
                    if "placements" in entry:
                        description += f"\n {name}: {utils.format_entry(entry)}"
                    else:
                        wins = entry["wins"]
                        losses = entry["losses"]                    
                        description += f"\n {name}: {utils.format_entry(entry)} (**{wins}/{losses}**)"

            # Create the embed
            who = summoner.riot_name if riot_id else "registered summoners"
            embed = {"title": f"Elo of {who}",  "color": configs.DARK_BLUE, "description": description}
            embed = discord.Embed.from_dict(embed)
            ts = utils.now().strftime(configs.DMYHMS_FORMAT)   
            embed.set_footer(text = ts)

            # Send the embed
            await context.channel.send(embed = embed)       


        @self.command()
        async def update(context):
            """Forces the LP update."""            
            message_log = lp_update.create_lp_update()
            await self.send_to_discord(message_log, self.lp_update_channel)            


        @self.command()
        async def restart(context):
            """Restarts mamie_bot."""            
            self.mamie_bot = mamieBot()
            

        @self.event
        async def on_command_error(context, e):
            """This is triggered upon a command error."""
            field_exception = {"name": "Exception", "value": (str(e))[:1000], "inline": True}
            fields_traceback = {"name": "Description", "value": (traceback.format_exc())[:1000], "inline": True}
            fields = [field_exception, fields_traceback]            
            embed = {"title": f"Command '{context.invoked_with}' failed (caught by on_command_error)", "fields": fields, "color": configs.DARK_BLUE}
            embed = discord.Embed.from_dict(embed)
            ts = utils.now().strftime(configs.DMYHMS_FORMAT)
            embed.set_footer(text = ts)                   
            await context.channel.send(embed = embed)
              

    async def setup_hook(self):
        """Starts the task to run in the background."""
        self.rename_tracker.start()        
        self.lp_tracker.start()        
        self.lp_updater.start()


    async def on_ready(self):
        """Sets up the channels."""
        
        # Setup the channels
        self.channels = [self.get_channel(channel_id) for channel_id in configs.DISCORD_CHANNEL_IDS]
        self.debug_channel = self.get_channel(configs.DISCORD_CHANNEL_ID_DEBUG)
        self.lp_update_channel = self.get_channel(configs.DISCORD_CHANNEL_LP_UPDATE)
        self.all_channels = self.channels + [self.debug_channel, self.lp_update_channel]        

        # Send a log-on message in local mode
        if configs.LOCAL:
            embed = {"title": "New connection", "description": f"Logged in as {self.user} (ID: {self.user.id})", "color": configs.YELLOW}
            embed = discord.Embed.from_dict(embed)
            ts = utils.now().strftime(configs.DMYHMS_FORMAT)   
            embed.set_footer(text = ts)
            for channel in self.all_channels:
                await channel.send(embed = embed)  


    async def send_to_discord(self, message_log, discord_channel):
        """Sends the embed in message_log to the discord channel indicated."""

        # Check if the message has not been sent already
        if not message_log["done_with"]:

            # Set the embed
            embed = discord.Embed.from_dict(message_log["embed"])

            # Set the fields (if any)
            if "fields" in message_log:
                for field in message_log["fields"]:
                    embed.add_field(name = field["name"], value = field["value"], inline = field["inline"])

            # Set the image (if any)
            if "image" in message_log:
                image = message_log["image"]
                bytes = BytesIO()
                image.save(bytes, format = "PNG")
                bytes.seek(0)
                file = discord.File(bytes, filename = "image.png")    
                embed.set_image(url = "attachment://image.png")            

            # Set the footer (if any)
            if "footer" in message_log:
                embed.set_footer(text = message_log["footer"])

            # Send the embed
            if "image" in message_log:
                msg = await discord_channel.send(embed = embed, file = file)
            else:
                msg = await discord_channel.send(embed = embed)

            # Set reactions (if any)
            if "reactions" in message_log:
                for reaction in message_log["reactions"]:
                    await msg.add_reaction(reaction)

            # Mark the message as sent
            message_log["done_with"] = True


    @tasks.loop(seconds = 60) 
    async def rename_tracker(self):
        """Sends a message whenever a summoner renames."""
        try:
            # Load the puuids and scout for changes
            change = False
            change_str = ""
            with open(configs.PUUID_PATH) as json_data:
                puuids = json.load(json_data)   
            for puuid in puuids:
                previous_name = puuids[puuid]
                summoner = Summoner(puuid = puuid)
                new_name = summoner.riot_name
                if new_name != previous_name:
                    puuids[puuid] = new_name
                    change = True
                    change_str += f"\n {previous_name} has renamed to {new_name}!"

            # Save the new puuids/names
            if change:
                with open(configs.PUUID_PATH, "w") as json_data:
                    json.dump(puuids, json_data)

                # Create the embed
                title = "Summoner name change"
                embed = {"title": title, "description": change_str, "color": configs.NAVY}    
                embed = discord.Embed.from_dict(embed)
                ts = utils.now().strftime(configs.DMYHMS_FORMAT)
                embed.set_footer(text = ts)

                # Send the embed
                for channel in self.all_channels:
                    await channel.send(embed = embed)  


        except Exception as e:
            field_exception = {"name": "Exception", "value": (str(e))[:1000], "inline": True}
            fields_traceback = {"name": "Description", "value": (traceback.format_exc())[:1000], "inline": True}
            fields = [field_exception, fields_traceback]
            embed = {"title": "rename_tracker failed", "color": configs.YELLOW, "fields": fields}
            embed = discord.Embed.from_dict(embed)
            ts = utils.now().strftime(configs.DMYHMS_FORMAT)   
            embed.set_footer(text = ts)
            await channel.send(embed = embed)                     


    # TODO: try except send_to_discord
    # TODO: why is an exception here not caught by on_command_error
    @tasks.loop(seconds = 5)
    async def lp_tracker(self):
        """Sends the message_logs received form mamie_bot to the Discord channels."""        
        self.mamie_bot.update()
        message_logs = self.mamie_bot.message_logs
        for message_log in message_logs:
            for channel_id in configs.DISCORD_CHANNEL_IDS:       
                try:     
                    channel = self.get_channel(channel_id if not message_log.get("bugged", False) else configs.DISCORD_CHANNEL_ID_DEBUG)
                    await self.send_to_discord(message_log, channel)
                except Exception as e:
                    field_message = {"name": "Message", "value": (str(message_log))[:1000], "inline": True}
                    field_exception = {"name": "Exception", "value": (str(e))[:1000], "inline": True}
                    fields_traceback = {"name": "Description", "value": (traceback.format_exc())[:1000], "inline": True}
                    fields = [field_message, field_exception, fields_traceback]             
                    embed = {"title": "lp_tracker failed", "fields": fields, "color": configs.DARK_BLUE}
                    embed = discord.Embed.from_dict(embed)
                    ts = utils.now().strftime(configs.DMYHMS_FORMAT)
                    embed.set_footer(text = ts)                   
                    await self.get_channel(configs.DISCORD_CHANNEL_ID_DEBUG).send(embed = embed)


    @tasks.loop(time = datetime.time(hour = 6, minute = 0, tzinfo = pytz.timezone("UTC"))) 
    async def lp_updater(self):
        """Sends to Discord, once a day Monday-Friday, a summary of the games played since the last update."""
        try:
            today = utils.now().weekday()
            if today not in [5, 6]:
                message_log = lp_update.create_lp_update()
                await self.send_to_discord(message_log, self.lp_update_channel)
        except Exception as e:
            field_exception = {"name": "Exception", "value": (str(e))[:1000], "inline": True}
            fields_traceback = {"name": "Description", "value": (traceback.format_exc())[:1000], "inline": True}
            fields = [field_exception, fields_traceback]                  
            embed = {"title": "lp_updater failed", "color": configs.DARK_BLUE, "fields": fields}
            embed = discord.Embed.from_dict(embed)
            ts = utils.now().strftime(configs.DMYHMS_FORMAT)   
            embed.set_footer(text = ts)
            await self.debug_channel.send(embed = embed)                    


    @rename_tracker.before_loop
    @lp_tracker.before_loop
    @lp_updater.before_loop
    async def before_my_task(self):
        """Makes it wait until the bot logs in."""
        await self.wait_until_ready()


####################
# RUN THE BOT
####################


intents = discord.Intents.default()
setattr(intents, "message_content", True)
client = MyClient(intents = intents)
try:
    client.loop.create_task(client.rename_tracker())
    client.loop.create_task(client.lp_tracker())
    client.loop.create_task(client.lp_updater())
    client.rename_tracker.start()
    client.lp_tracker.start()
    client.lp_updater.start()
except:
    pass
client.run(configs.DISCORD_TOKEN)
