

from summoner import Summoner
from game import Game

riot_id = {"game_name": "katare", "tagline": "euw"}
summoner = Summoner(riot_id = riot_id)
summoner.puuid
x = summoner.get_last_played_game("1100")
game_data = x["info"]
participants = game_data["participants"]
for participant in participants:
    if participant["puuid"] == summoner.puuid:
        break
self = Game(game_data, summoner = summoner)
self.has_ended()

image = self.in_game_message_log()["image"]
image = self.out_of_game_message_log()["image"]



import pip
pip.main(["install", "pandas"])

pip.

def f(x, y):
    return x*y
from functools import reduce
reduce(f, [3, 4, 5])

l = [1, 2, 3]
for x in l:
    print(x)
    if x == 2:
        l.remove(x)
