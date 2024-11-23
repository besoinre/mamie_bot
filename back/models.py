from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Augment:
    name: str
    stars: int

@dataclass
class GameInfo:
    rounds: int
    result: str
    new_rating: str
    top_comp: str
    placement: int
    duration: int  # Consider using timedelta if you need to do time calculations
    augments: List[Augment]

@dataclass
class LiveEvent:
    player: str
    rank: str
    status: str  # 'entered' or 'exited' (consider using Enum for strict type safety)
    timestamp: str  # Alternatively, use datetime.datetime for actual date/time
    game_info: Optional[GameInfo] = None
