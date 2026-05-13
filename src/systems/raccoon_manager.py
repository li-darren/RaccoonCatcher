import random
from src.entities.raccoon import Raccoon
from settings import NUM_ZONES

_SIZES = ["small", "medium", "large", "xl"]
_WEIGHTS_BY_LEVEL = {
    1: [0.50, 0.30, 0.15, 0.05],
    2: [0.35, 0.35, 0.20, 0.10],
    3: [0.20, 0.30, 0.30, 0.20],
}


class RaccoonManager:
    def __init__(self, game):
        self.game = game
        self.raccoons: list = []

    def populate(self, level_config):
        self.raccoons.clear()
        weights = _WEIGHTS_BY_LEVEL.get(level_config.level_num, _WEIGHTS_BY_LEVEL[3])
        zones = list(range(NUM_ZONES))
        random.shuffle(zones)

        for i in range(level_config.raccoon_count):
            size = random.choices(_SIZES, weights=weights, k=1)[0]
            zone = zones[i % NUM_ZONES]
            r = Raccoon(size, zone,
                        wariness_scale=level_config.wariness_scale,
                        speed_scale=level_config.speed_scale)
            # Stagger timers so raccoons don't all hop simultaneously
            r.move_timer *= 0.3 + 0.7 * (i / max(level_config.raccoon_count, 1))
            self.raccoons.append(r)

    def update(self, dt: float):
        if self.game.raccoons_paused:
            return
        for r in self.raccoons:
            r.update(dt)
            r.update_wander(dt)

    def update_wander_only(self, dt: float):
        """Tick camera wandering without zone-hopping (used while player watches cameras)."""
        for r in self.raccoons:
            r.update_wander(dt)

    def get_raccoon_in_zone(self, zone_index: int):
        for r in self.raccoons:
            if r.zone_index == zone_index:
                return r
        return None

    def raccoons_in_zone(self, zone_index: int) -> list:
        return [r for r in self.raccoons if r.zone_index == zone_index]

    def remove(self, raccoon: Raccoon):
        if raccoon in self.raccoons:
            self.raccoons.remove(raccoon)

    def respawn_if_needed(self, exclude_zone: int = -1):
        lc = self.game.level_config
        weights = _WEIGHTS_BY_LEVEL.get(lc.level_num, _WEIGHTS_BY_LEVEL[3])
        while len(self.raccoons) < lc.raccoon_count:
            size = random.choices(_SIZES, weights=weights, k=1)[0]
            available = [z for z in range(NUM_ZONES) if z != exclude_zone]
            zone = random.choice(available)
            self.raccoons.append(
                Raccoon(size, zone,
                        wariness_scale=lc.wariness_scale,
                        speed_scale=lc.speed_scale)
            )
