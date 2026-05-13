import pygame
from dataclasses import dataclass
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, NUM_ZONES, ZONE_NAMES,
    CAMERA_PAD, CAMERA_FEED_W, CAMERA_FEED_H, HUD_BAR_H,
)


@dataclass
class Zone:
    index: int
    name: str
    camera_rect: pygame.Rect
    yard_rect: pygame.Rect
    bg_color: tuple
    prop_color: tuple


class ZoneManager:
    def __init__(self):
        self.zones = self._build_zones()

    def _build_zones(self):
        positions = []
        for row in range(2):
            for col in range(2):
                x = CAMERA_PAD + col * (CAMERA_FEED_W + CAMERA_PAD)
                y = HUD_BAR_H + CAMERA_PAD + row * (CAMERA_FEED_H + CAMERA_PAD)
                positions.append(pygame.Rect(x, y, CAMERA_FEED_W, CAMERA_FEED_H))

        yard_rect = pygame.Rect(0, HUD_BAR_H, SCREEN_WIDTH, SCREEN_HEIGHT - HUD_BAR_H)

        colors = [
            ((40, 80, 40),  (100, 60, 30)),   # Front Yard
            ((30, 60, 30),  (80, 80, 80)),     # Back Yard
            ((50, 90, 50),  (120, 100, 40)),   # Side Gate
            ((35, 70, 35),  (60, 40, 20)),     # Garden Shed
        ]

        return [
            Zone(
                index=i,
                name=ZONE_NAMES[i],
                camera_rect=positions[i],
                yard_rect=yard_rect,
                bg_color=colors[i][0],
                prop_color=colors[i][1],
            )
            for i in range(NUM_ZONES)
        ]

    def get_zone(self, index: int) -> Zone:
        return self.zones[index]
