import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
if not pygame.get_init():
    pygame.init()

from src.systems.zone_manager import ZoneManager
from settings import NUM_ZONES, HUD_BAR_H, SCREEN_WIDTH, SCREEN_HEIGHT


class TestZoneManager:
    def setup_method(self):
        self.zm = ZoneManager()

    def test_correct_number_of_zones(self):
        assert len(self.zm.zones) == NUM_ZONES

    def test_get_zone_returns_zone(self):
        from src.systems.zone_manager import Zone
        assert isinstance(self.zm.get_zone(0), Zone)

    def test_zone_indices_match(self):
        for i, zone in enumerate(self.zm.zones):
            assert zone.index == i

    def test_all_zones_have_names(self):
        for zone in self.zm.zones:
            assert isinstance(zone.name, str) and len(zone.name) > 0

    def test_yard_rect_starts_below_hud(self):
        for zone in self.zm.zones:
            assert zone.yard_rect.top == HUD_BAR_H

    def test_yard_rect_fills_width(self):
        for zone in self.zm.zones:
            assert zone.yard_rect.width == SCREEN_WIDTH

    def test_yard_rect_height(self):
        for zone in self.zm.zones:
            assert zone.yard_rect.height == SCREEN_HEIGHT - HUD_BAR_H

    def test_all_zones_share_same_yard_rect_dimensions(self):
        rects = [zone.yard_rect for zone in self.zm.zones]
        assert all(r.width == rects[0].width for r in rects)
        assert all(r.height == rects[0].height for r in rects)

    def test_camera_rects_are_pygame_rects(self):
        import pygame
        for zone in self.zm.zones:
            assert isinstance(zone.camera_rect, pygame.Rect)

    def test_camera_rects_do_not_overlap(self):
        rects = [zone.camera_rect for zone in self.zm.zones]
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                assert not rects[i].colliderect(rects[j]), \
                    f"Zones {i} and {j} camera rects overlap"

    def test_camera_rects_are_below_hud(self):
        for zone in self.zm.zones:
            assert zone.camera_rect.top >= HUD_BAR_H

    def test_bg_and_prop_colors_are_tuples(self):
        for zone in self.zm.zones:
            assert isinstance(zone.bg_color, tuple)
            assert isinstance(zone.prop_color, tuple)
