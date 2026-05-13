import random
from settings import RACCOON_SIZES, NUM_ZONES


class Raccoon:
    def __init__(self, size: str, zone_index: int,
                 wariness_scale: float = 1.0, speed_scale: float = 1.0):
        self.size = size
        cfg = RACCOON_SIZES[size]
        self.radius: int = cfg["radius"]
        self.points: int = cfg["points"]
        self.wariness: float = min(cfg["wariness"] * wariness_scale, 0.97)

        lo, hi = cfg["move_range"]
        lo = max(lo * speed_scale, 1.0)
        hi = max(hi * speed_scale, 2.0)
        self.move_range = (lo, hi)

        self.zone_index: int = zone_index
        self.move_timer: float = random.uniform(*self.move_range)
        self.yard_pos: tuple = (0, 0)

    def update(self, dt: float) -> bool:
        """Tick movement timer. Returns True when the raccoon changes zones."""
        self.move_timer -= dt
        if self.move_timer <= 0:
            available = [z for z in range(NUM_ZONES) if z != self.zone_index]
            self.zone_index = random.choice(available)
            self.move_timer = random.uniform(*self.move_range)
            return True
        return False

    def set_yard_position(self, yard_rect):
        margin = self.radius + 20
        x = random.randint(yard_rect.left + margin, yard_rect.right - margin)
        # Keep raccoon in the lower two-thirds of the yard (on the grass)
        grass_top = yard_rect.top + yard_rect.height // 3 + margin + 30
        y = random.randint(grass_top, yard_rect.bottom - margin - 60)
        self.yard_pos = (x, y)

    def flee_probability(self, seconds_in_camera: float) -> float:
        """Chance the raccoon bolts before the player arrives."""
        base = self.wariness * min(seconds_in_camera / 60.0, 1.0)
        return min(base, 0.95)
