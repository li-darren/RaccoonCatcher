from dataclasses import dataclass
from typing import List


@dataclass
class LevelConfig:
    level_num: int
    score_target: int
    time_limit_sec: float
    raccoon_count: int
    wariness_scale: float   # multiplied onto each raccoon's base wariness
    speed_scale: float      # multiplied onto move interval (lower = hops faster)


LEVELS: List[LevelConfig] = [
    LevelConfig(
        level_num=1, score_target=100, time_limit_sec=180.0,
        raccoon_count=1, wariness_scale=1.0, speed_scale=1.0,
    ),
    LevelConfig(
        level_num=2, score_target=250, time_limit_sec=180.0,
        raccoon_count=1, wariness_scale=1.2, speed_scale=0.75,
    ),
    LevelConfig(
        level_num=3, score_target=500, time_limit_sec=180.0,
        raccoon_count=1, wariness_scale=1.5, speed_scale=0.55,
    ),
]
