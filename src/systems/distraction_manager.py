import random
from src.entities.bird import Bird
from src.entities.leaf import Leaf
from src.entities.trash_bag import TrashBag
from settings import BIRD_SPAWN_INTERVAL, BIRD_MAX_PER_ZONE, LEAF_SPAWN_INTERVAL, LEAF_MAX_PER_ZONE


class DistractionManager:
    def __init__(self):
        self.birds: list = []
        self.leaves: list = []
        self.trash_bags: list = []
        self._bird_timers: list = []
        self._leaf_timers: list = []

    def reset(self, num_zones: int):
        self.birds.clear()
        self.leaves.clear()
        self.trash_bags = [TrashBag(i) for i in range(num_zones)]
        self._bird_timers = [random.uniform(*BIRD_SPAWN_INTERVAL) for _ in range(num_zones)]
        self._leaf_timers = [random.uniform(*LEAF_SPAWN_INTERVAL) for _ in range(num_zones)]

    def update(self, dt: float):
        self.birds = [b for b in self.birds if not b.update(dt)]
        self.leaves = [lf for lf in self.leaves if not lf.update(dt)]

        for zone_i in range(len(self._bird_timers)):
            self._bird_timers[zone_i] -= dt
            if self._bird_timers[zone_i] <= 0:
                if sum(1 for b in self.birds if b.zone_index == zone_i) < BIRD_MAX_PER_ZONE:
                    self.birds.append(Bird(zone_i))
                self._bird_timers[zone_i] = random.uniform(*BIRD_SPAWN_INTERVAL)

            self._leaf_timers[zone_i] -= dt
            if self._leaf_timers[zone_i] <= 0:
                if sum(1 for lf in self.leaves if lf.zone_index == zone_i) < LEAF_MAX_PER_ZONE:
                    self.leaves.append(Leaf(zone_i))
                self._leaf_timers[zone_i] = random.uniform(*LEAF_SPAWN_INTERVAL)

    def birds_in_zone(self, zone_index: int) -> list:
        return [b for b in self.birds if b.zone_index == zone_index]

    def leaves_in_zone(self, zone_index: int) -> list:
        return [lf for lf in self.leaves if lf.zone_index == zone_index]

    def trash_bags_in_zone(self, zone_index: int) -> list:
        return [bag for bag in self.trash_bags if bag.zone_index == zone_index]
