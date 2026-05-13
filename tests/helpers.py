"""Shared fake objects for state tests."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
if not pygame.get_init():
    pygame.init()

from src.systems.level_config import LevelConfig


class FakeRect:
    def __init__(self, left, top, width, height):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.right = left + width
        self.bottom = top + height

    def __repr__(self):
        return f"FakeRect({self.left}, {self.top}, {self.width}, {self.height})"


class FakeZone:
    def __init__(self, index=0, name="Test Zone"):
        self.index = index
        self.name = name
        self.yard_rect = FakeRect(0, 50, 1280, 670)
        self.camera_rect = FakeRect(10, 60, 320, 240)
        self.bg_color = (40, 80, 40)
        self.prop_color = (100, 60, 30)


class FakeZoneManager:
    def __init__(self, num_zones=4):
        self.zones = [FakeZone(i, f"Zone {i}") for i in range(num_zones)]

    def get_zone(self, index):
        return self.zones[index]


class FakeRaccoon:
    def __init__(self, zone_index=0, points=50):
        self.zone_index = zone_index
        self.points = points
        self.radius = 18
        self.size = "medium"
        self.facing_right = True
        self.yard_pos = [300.0, 400.0]
        self.yard_vx = 80.0

    def set_yard_position_from_camera(self, yard_rect, duration_sec):
        pass


class FakeRaccoonManager:
    def __init__(self, raccoons=None):
        self._raccoons = raccoons or []

    def raccoons_in_zone(self, zone_index):
        return [r for r in self._raccoons if r.zone_index == zone_index]

    def respawn_if_needed(self, exclude_zone=-1):
        pass

    def update(self, dt):
        pass

    def remove(self, raccoon):
        if raccoon in self._raccoons:
            self._raccoons.remove(raccoon)


class FakeDistractionManager:
    def update(self, dt):
        pass

    def birds_in_zone(self, i):
        return []

    def leaves_in_zone(self, i):
        return []

    def trash_bags_in_zone(self, i):
        return []

    def reset(self, num_zones):
        pass


class FakeGame:
    """Minimal game object sufficient for all state tests."""

    def __init__(self, level=1, score=0, timer=180.0, score_target=100):
        self.level = level
        self.score = score
        self.timer_remaining = timer
        self.raccoons_paused = False
        self.target_zone = 0

        self.level_config = LevelConfig(
            level_num=level, score_target=score_target,
            time_limit_sec=180.0, raccoon_count=1,
            wariness_scale=1.0, speed_scale=1.0,
        )
        self.zone_manager = FakeZoneManager()
        self.raccoon_manager = FakeRaccoonManager()
        self.distraction_manager = FakeDistractionManager()

        self._state_changes = []

    def change_state(self, name, **kwargs):
        self._state_changes.append((name, kwargs))

    def reset_level(self, level_num):
        self.level = level_num

    @property
    def last_state_change(self):
        return self._state_changes[-1] if self._state_changes else None
